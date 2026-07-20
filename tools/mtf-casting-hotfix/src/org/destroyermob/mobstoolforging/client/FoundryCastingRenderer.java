package org.destroyermob.mobstoolforging.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.destroyermob.mobstoolforging.world.FoundryCastingBlockEntity;
import org.joml.Vector3f;

public class FoundryCastingRenderer implements BlockEntityRenderer<FoundryCastingBlockEntity> {
    private static final ResourceLocation MOLTEN_TEXTURE = ResourceLocation.fromNamespaceAndPath(
            "mobstoolforging", "block/molten_still"
    );
    private static final float TABLE_FORM_Y = 0.946875F;
    private static final float TABLE_OUTPUT_Y = 0.95F;
    private static final float TABLE_FLUID_BOTTOM = 0.940625F;
    private static final float TABLE_FLUID_HEIGHT = 0.04375F;
    private static final float BASIN_FLUID_BOTTOM = 0.190625F;
    private static final float BASIN_FLUID_HEIGHT = 0.79375F;
    private final ItemRenderer itemRenderer = Minecraft.getInstance().getItemRenderer();

    public FoundryCastingRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public void render(FoundryCastingBlockEntity casting, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffers, int light, int overlay) {
        boolean basin = FoundryCastingBlockEntity.isBasin(casting.getBlockState());
        float formY = basin ? 0.78F : TABLE_FORM_Y;
        float outputY = basin ? 0.82F : TABLE_OUTPUT_Y;
        ItemStack form = casting.form();
        if (!form.isEmpty()) {
            renderItem(casting, form, poseStack, buffers, light, overlay, formY, 0.7F);
        }

        float coolingProgress = coolingProgress(casting, partialTick);
        float fluidOpacity = coolingProgress <= 0.75F
                ? 1.0F
                : Mth.clamp(1.0F - (coolingProgress - 0.75F) / 0.25F, 0.0F, 1.0F);
        casting.material().ifPresent(material -> renderFluid(casting, material, fluidOpacity, poseStack, buffers, overlay));

        ItemStack output = casting.output();
        if (!output.isEmpty()) {
            renderItem(casting, output, poseStack, buffers, light, overlay, outputY, 0.7F);
        } else if (coolingProgress > 0.0F) {
            ItemStack preview = casting.previewOutput();
            if (!preview.isEmpty()) {
                MultiBufferSource coolingBuffers = new CoolingBufferSource(buffers, coolingProgress, fluidOpacity);
                renderItem(casting, preview, poseStack, coolingBuffers, light, overlay, outputY, 0.7F);
            }
        }
    }

    private static float coolingProgress(FoundryCastingBlockEntity casting, float partialTick) {
        return casting.coolingTicks() > 0 && casting.amountMb() >= casting.capacityMb()
                ? Mth.clamp((casting.coolingTicks() + partialTick) / 60.0F, 0.0F, 1.0F)
                : 0.0F;
    }

    private void renderItem(FoundryCastingBlockEntity casting, ItemStack stack, PoseStack poseStack,
                            MultiBufferSource buffers, int light, int overlay, float y, float scale) {
        poseStack.pushPose();
        poseStack.translate(0.5F, y, 0.5F);
        poseStack.mulPose(Axis.XP.rotationDegrees(270.0F));
        poseStack.scale(scale, scale, scale);
        itemRenderer.renderStatic(stack, ItemDisplayContext.FIXED, light, overlay, poseStack, buffers, casting.getLevel(), 0);
        poseStack.popPose();
    }

    private static void renderFluid(FoundryCastingBlockEntity casting, ResourceLocation material, float opacity,
                                    PoseStack poseStack, MultiBufferSource buffers, int overlay) {
        if (opacity <= 0.0F) {
            return;
        }
        boolean basin = FoundryCastingBlockEntity.isBasin(casting.getBlockState());
        float min = 0.065625F;
        float max = 0.934375F;
        float bottom = basin ? BASIN_FLUID_BOTTOM : TABLE_FLUID_BOTTOM;
        float height = basin ? BASIN_FLUID_HEIGHT : TABLE_FLUID_HEIGHT;
        float y = bottom + height * Mth.clamp(casting.fillFraction(), 0.0F, 1.0F);

        TextureAtlasSprite sprite = Minecraft.getInstance().getTextureAtlas(TextureAtlas.LOCATION_BLOCKS).apply(MOLTEN_TEXTURE);
        VertexConsumer consumer = buffers.getBuffer(RenderType.entityTranslucent(TextureAtlas.LOCATION_BLOCKS));
        int baseColor = FoundryForgeRenderer.moltenColor(material);
        int color = Mth.clamp(Math.round((baseColor >>> 24 & 0xFF) * opacity), 0, 255) << 24 | baseColor & 0xFFFFFF;
        Vector3f normal = Direction.UP.step();
        float u0 = sprite.getU(0.0F);
        float v0 = sprite.getV(0.0F);
        float u1 = sprite.getU(max - min);
        float v1 = sprite.getV(max - min);
        vertex(poseStack, consumer, normal, color, min, y, min, u0, v1, overlay);
        vertex(poseStack, consumer, normal, color, min, y, max, u0, v0, overlay);
        vertex(poseStack, consumer, normal, color, max, y, max, u1, v0, overlay);
        vertex(poseStack, consumer, normal, color, max, y, min, u1, v1, overlay);
    }

    private static void vertex(PoseStack poseStack, VertexConsumer consumer, Vector3f normal, int color,
                               float x, float y, float z, float u, float v, int overlay) {
        consumer.addVertex(poseStack.last(), x, y, z)
                .setColor(color >>> 16 & 0xFF, color >>> 8 & 0xFF, color & 0xFF, color >>> 24 & 0xFF)
                .setUv(u, v)
                .setOverlay(overlay)
                .setLight(0xF000F0)
                .setNormal(poseStack.last(), normal.x(), normal.y(), normal.z());
    }

    private static final class CoolingBufferSource implements MultiBufferSource {
        private final MultiBufferSource inner;
        private final int red;
        private final int green;
        private final int blue;
        private final int alpha;

        private CoolingBufferSource(MultiBufferSource inner, float opacity, float temperature) {
            this.inner = inner;
            this.alpha = Mth.clamp(Math.round(opacity * 255.0F), 0, 255);
            int heat = Mth.clamp(Math.round(temperature * 255.0F), 0, 255);
            this.red = 255 - heat * 79 / 255;
            this.green = 255 - heat * 159 / 255;
            this.blue = 255 - heat * 223 / 255;
        }

        @Override
        public VertexConsumer getBuffer(RenderType ignored) {
            VertexConsumer consumer = inner.getBuffer(RenderType.entityTranslucent(TextureAtlas.LOCATION_BLOCKS));
            return new CoolingVertexConsumer(consumer, red, green, blue, alpha);
        }
    }

    private static final class CoolingVertexConsumer implements VertexConsumer {
        private final VertexConsumer inner;
        private final int red;
        private final int green;
        private final int blue;
        private final int alpha;

        private CoolingVertexConsumer(VertexConsumer inner, int red, int green, int blue, int alpha) {
            this.inner = inner;
            this.red = red;
            this.green = green;
            this.blue = blue;
            this.alpha = alpha;
        }

        @Override
        public VertexConsumer addVertex(float x, float y, float z) {
            inner.addVertex(x, y, z);
            return this;
        }

        @Override
        public VertexConsumer setColor(int red, int green, int blue, int alpha) {
            inner.setColor(red * this.red / 255, green * this.green / 255,
                    blue * this.blue / 255, alpha * this.alpha / 255);
            return this;
        }

        @Override
        public VertexConsumer setUv(float u, float v) {
            inner.setUv(u, v);
            return this;
        }

        @Override
        public VertexConsumer setUv1(int u, int v) {
            inner.setUv1(u, v);
            return this;
        }

        @Override
        public VertexConsumer setUv2(int u, int v) {
            inner.setUv2(u, v);
            return this;
        }

        @Override
        public VertexConsumer setNormal(float x, float y, float z) {
            inner.setNormal(x, y, z);
            return this;
        }
    }
}
