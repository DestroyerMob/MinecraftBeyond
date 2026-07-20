package org.destroyermob.mobstoolforging.world;

import com.mojang.serialization.MapCodec;
import java.util.Optional;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.destroyermob.mobstoolforging.registry.ModBlocks;

public class FoundryFaucetBlock extends BaseEntityBlock {
    public static final MapCodec<FoundryFaucetBlock> CODEC = simpleCodec(FoundryFaucetBlock::new);
    public static final DirectionProperty FACING = HorizontalDirectionalBlock.FACING;
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");
    private static final int POUR_RATE_MB = 10;
    private static final int POUR_INTERVAL = 4;

    // The model is a short U-shaped channel attached to the wall opposite FACING.
    private static final VoxelShape NORTH_SHAPE = Shapes.or(
            Block.box(6.0, 7.0, 12.0, 10.0, 8.0, 16.0),
            Block.box(6.0, 8.0, 12.0, 7.0, 9.0, 16.0),
            Block.box(9.0, 8.0, 12.0, 10.0, 9.0, 16.0)
    );
    private static final VoxelShape SOUTH_SHAPE = Shapes.or(
            Block.box(6.0, 7.0, 0.0, 10.0, 8.0, 4.0),
            Block.box(6.0, 8.0, 0.0, 7.0, 9.0, 4.0),
            Block.box(9.0, 8.0, 0.0, 10.0, 9.0, 4.0)
    );
    private static final VoxelShape EAST_SHAPE = Shapes.or(
            Block.box(0.0, 7.0, 6.0, 4.0, 8.0, 10.0),
            Block.box(0.0, 8.0, 6.0, 4.0, 9.0, 7.0),
            Block.box(0.0, 8.0, 9.0, 4.0, 9.0, 10.0)
    );
    private static final VoxelShape WEST_SHAPE = Shapes.or(
            Block.box(12.0, 7.0, 6.0, 16.0, 8.0, 10.0),
            Block.box(12.0, 8.0, 6.0, 16.0, 9.0, 7.0),
            Block.box(12.0, 8.0, 9.0, 16.0, 9.0, 10.0)
    );

    public FoundryFaucetBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(ACTIVE, false));
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new FoundryFaucetBlockEntity(pos, state);
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction face = context.getClickedFace();
        return !face.getAxis().isHorizontal()
                ? null
                : defaultBlockState().setValue(FACING, face)
                        .setValue(ACTIVE, context.getLevel().hasNeighborSignal(context.getClickedPos()));
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hitResult) {
        if (!level.isClientSide) {
            boolean active = !state.getValue(ACTIVE);
            level.setBlock(pos, state.setValue(ACTIVE, active), 3);
            if (active) {
                level.scheduleTick(pos, this, 1);
            } else if (level.getBlockEntity(pos) instanceof FoundryFaucetBlockEntity faucet) {
                faucet.setPouringMaterial(null);
            }
            level.playSound(null, pos, SoundEvents.LEVER_CLICK, SoundSource.BLOCKS, 0.35F, active ? 0.7F : 0.55F);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock, BlockPos neighborPos, boolean movedByPiston) {
        if (!level.isClientSide && level.hasNeighborSignal(pos) && !state.getValue(ACTIVE)) {
            level.setBlock(pos, state.setValue(ACTIVE, true), 3);
            level.scheduleTick(pos, this, 1);
        }
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (!state.getValue(ACTIVE)) {
            clearPouringMaterial(level, pos);
            return;
        }
        ResourceLocation material = pour(level, pos, state);
        if (material == null) {
            stopPouring(level, pos, state);
            return;
        }
        if (level.getBlockEntity(pos) instanceof FoundryFaucetBlockEntity faucet) {
            faucet.setPouringMaterial(material);
        }
        level.scheduleTick(pos, this, POUR_INTERVAL);
    }

    private static void stopPouring(ServerLevel level, BlockPos pos, BlockState state) {
        clearPouringMaterial(level, pos);
        if (state.getValue(ACTIVE)) {
            level.setBlock(pos, state.setValue(ACTIVE, false), 3);
        }
    }

    private static void clearPouringMaterial(Level level, BlockPos pos) {
        if (level.getBlockEntity(pos) instanceof FoundryFaucetBlockEntity faucet) {
            faucet.setPouringMaterial(null);
        }
    }

    @Nullable
    private static ResourceLocation pour(ServerLevel level, BlockPos pos, BlockState state) {
        Direction facing = state.getValue(FACING);
        BlockPos drainPos = pos.relative(facing.getOpposite());
        BlockState drainState = level.getBlockState(drainPos);
        if (!drainState.is(ModBlocks.FOUNDRY_DRAIN.get())
                || !(level.getBlockEntity(pos.below()) instanceof FoundryCastingBlockEntity receiver)) {
            return null;
        }
        return FoundryAccess.findController(level, drainPos).flatMap(forge -> forge.bottomMoltenMaterial().flatMap(material -> {
            int amount = Math.min(POUR_RATE_MB, receiver.remainingCapacity(material));
            if (amount <= 0) {
                return Optional.empty();
            }
            int drained = forge.drainBottom(material, amount);
            if (drained <= 0) {
                return Optional.empty();
            }
            receiver.receive(material, drained);
            level.playSound(null, pos, SoundEvents.BUCKET_EMPTY_LAVA, SoundSource.BLOCKS, 0.08F, 1.8F);
            return Optional.of(material);
        })).orElse(null);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return switch (state.getValue(FACING)) {
            case SOUTH -> SOUTH_SHAPE;
            case EAST -> EAST_SHAPE;
            case WEST -> WEST_SHAPE;
            default -> NORTH_SHAPE;
        };
    }

    @Override
    protected BlockState rotate(BlockState state, Rotation rotation) {
        return state.setValue(FACING, rotation.rotate(state.getValue(FACING)));
    }

    @Override
    protected BlockState mirror(BlockState state, Mirror mirror) {
        return state.rotate(mirror.getRotation(state.getValue(FACING)));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, ACTIVE);
    }
}
