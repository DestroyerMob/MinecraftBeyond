package org.destroyermob.mobstoolforging.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.destroyermob.mobstoolforging.world.FoundryCastingBlockEntity;
import org.destroyermob.mobstoolforging.world.FoundryFaucetBlock;
import org.destroyermob.mobstoolforging.world.FoundryFaucetBlockEntity;
import org.joml.Vector3f;

public class FoundryFaucetRenderer implements BlockEntityRenderer<FoundryFaucetBlockEntity> {
    private static final ResourceLocation FLOWING_MOLTEN_TEXTURE = ResourceLocation.fromNamespaceAndPath(
            "mobstoolforging", "block/molten_liquid"
    );
    private static final float HALF_WIDTH = 0.055F;
    private static final float STREAM_WIDTH = HALF_WIDTH * 2.0F;
    private static final float STREAM_TOP = 7.0F / 16.0F;

    public FoundryFaucetRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public boolean shouldRenderOffScreen(FoundryFaucetBlockEntity faucet) {
        return true;
    }

    @Override
    public void render(FoundryFaucetBlockEntity faucet, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffers, int light, int overlay) {
        if (faucet.getBlockState().getValue(FoundryFaucetBlock.ACTIVE)) {
            faucet.pouringMaterial().ifPresent(material -> renderStream(faucet, material, poseStack, buffers, overlay));
        }
    }

    private static void renderStream(FoundryFaucetBlockEntity faucet, ResourceLocation material,
                                     PoseStack poseStack, MultiBufferSource buffers, int overlay) {
        Direction facing = faucet.getBlockState().getValue(FoundryFaucetBlock.FACING);

        // The stream falls from the open end of the short wall-mounted channel.
        float centerX = facing == Direction.EAST ? 0.25F : facing == Direction.WEST ? 0.75F : 0.5F;
        float centerZ = facing == Direction.SOUTH ? 0.25F : facing == Direction.NORTH ? 0.75F : 0.5F;
        float bottom = streamBottom(faucet);
        float minX = centerX - HALF_WIDTH;
        float maxX = centerX + HALF_WIDTH;
        float minZ = centerZ - HALF_WIDTH;
        float maxZ = centerZ + HALF_WIDTH;

        TextureAtlasSprite sprite = Minecraft.getInstance().getTextureAtlas(TextureAtlas.LOCATION_BLOCKS).apply(FLOWING_MOLTEN_TEXTURE);
        VertexConsumer consumer = buffers.getBuffer(RenderType.entityTranslucent(TextureAtlas.LOCATION_BLOCKS));
        int color = FoundryForgeRenderer.moltenColor(material);
        float u0 = sprite.getU(0.0F);
        float v0 = sprite.getV(0.0F);
        float u1 = sprite.getU(STREAM_WIDTH);
        float v1 = sprite.getV(STREAM_TOP - bottom);

        quad(poseStack, consumer, Direction.NORTH, color, overlay,
                minX, bottom, minZ, u0, v1, maxX, bottom, minZ, u1, v1,
                maxX, STREAM_TOP, minZ, u1, v0, minX, STREAM_TOP, minZ, u0, v0);
        quad(poseStack, consumer, Direction.SOUTH, color, overlay,
                maxX, bottom, maxZ, u0, v1, minX, bottom, maxZ, u1, v1,
                minX, STREAM_TOP, maxZ, u1, v0, maxX, STREAM_TOP, maxZ, u0, v0);
        quad(poseStack, consumer, Direction.WEST, color, overlay,
                minX, bottom, maxZ, u0, v1, minX, bottom, minZ, u1, v1,
                minX, STREAM_TOP, minZ, u1, v0, minX, STREAM_TOP, maxZ, u0, v0);
        quad(poseStack, consumer, Direction.EAST, color, overlay,
                maxX, bottom, minZ, u0, v1, maxX, bottom, maxZ, u1, v1,
                maxX, STREAM_TOP, maxZ, u1, v0, maxX, STREAM_TOP, minZ, u0, v0);
    }

    private static float streamBottom(FoundryFaucetBlockEntity faucet) {
        if (faucet.getLevel() == null
                || !(faucet.getLevel().getBlockEntity(faucet.getBlockPos().below()) instanceof FoundryCastingBlockEntity casting)) {
            return 0.0F;
        }
        float fill = Mth.clamp(casting.fillFraction(), 0.0F, 1.0F);
        if (FoundryCastingBlockEntity.isBasin(casting.getBlockState())) {
            return 0.190625F + 0.79375F * fill - 1.0F;
        }
        return 0.940625F + 0.04375F * fill - 1.0F;
    }

    private static void quad(PoseStack poseStack, VertexConsumer consumer, Direction direction, int color, int overlay,
                             float x1, float y1, float z1, float u1, float v1,
                             float x2, float y2, float z2, float u2, float v2,
                             float x3, float y3, float z3, float u3, float v3,
                             float x4, float y4, float z4, float u4, float v4) {
        Vector3f normal = direction.step();
        vertex(poseStack, consumer, normal, color, overlay, x1, y1, z1, u1, v1);
        vertex(poseStack, consumer, normal, color, overlay, x2, y2, z2, u2, v2);
        vertex(poseStack, consumer, normal, color, overlay, x3, y3, z3, u3, v3);
        vertex(poseStack, consumer, normal, color, overlay, x4, y4, z4, u4, v4);
    }

    private static void vertex(PoseStack poseStack, VertexConsumer consumer, Vector3f normal, int color, int overlay,
                               float x, float y, float z, float u, float v) {
        consumer.addVertex(poseStack.last(), x, y, z)
                .setColor(color >>> 16 & 0xFF, color >>> 8 & 0xFF, color & 0xFF, color >>> 24 & 0xFF)
                .setUv(u, v)
                .setOverlay(overlay)
                .setLight(0xF000F0)
                .setNormal(poseStack.last(), normal.x(), normal.y(), normal.z());
    }
}
