// Recipe-specific prepared mixtures let full 3x3 baked recipes use the
// reusable Bakery tray without discarding their ninth real ingredient.
var FOOD_LARGE_BAKING_RECIPE_IDS = [
  'bountifulfares:cocoa_cake',
  'bountifulfares:coconut_cake',
  'bountifulfares:sponge_cake',
  'brewinandchewin:quiche_from_bacon',
  'brewinandchewin:quiche_from_mushroom',
  'croptopia:pumpkin_bars',
  'ends_delight:food/chorus_fruit_pie',
  'expandeddelight:cranberry_cobbler',
  'expandeddelight:honeyed_goat_cheese_tart',
  'farmersdelight:apple_pie',
  'farmersdelight:chocolate_pie',
  'farmersdelight:shepherds_pie_block',
  'farmersdelight:sweet_berry_cheesecake',
  'mynethersdelight:crafting/magma_cake'
]

function foodBakingIntermediatePath(recipeId) {
  return `food_unification_baking_${String(recipeId).replace(/[:\/.]/g, '_')}`
}

function foodBakingIntermediateName(recipeId) {
  var path = String(recipeId).substring(String(recipeId).indexOf(':') + 1)
  var leaf = path.substring(path.lastIndexOf('/') + 1)
  return leaf
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.substring(1))
    .join(' ')
}

StartupEvents.registry('item', event => {
  FOOD_LARGE_BAKING_RECIPE_IDS.forEach(recipeId => {
    event.create(foodBakingIntermediatePath(recipeId))
      .displayName(`Prepared ${foodBakingIntermediateName(recipeId)} Mixture`)
      .maxStackSize(16)
      .texture('bakery:item/sweet_dough')
  })
})
