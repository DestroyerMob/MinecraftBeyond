// Recipe-specific prepared bases preserve every ingredient in meals that are
// larger than the chosen cooking pot or roaster can accept in one operation.
var FOOD_STAGED_STATION_RECIPE_IDS = [
  'croptopia:cabbage_roll',
  'croptopia:shaped_stuffed_artichoke',
  'croptopia:the_big_breakfast',
  'pamhc2foodcore:sprinklesdonutitem',
  'pamhc2foodextended:beancornmealitem',
  'pamhc2foodextended:bulgogiitem',
  'pamhc2foodextended:cantonesenoodlesitem',
  'pamhc2foodextended:chickengumboitem',
  'pamhc2foodextended:chikorollitem',
  'pamhc2foodextended:cornedbeefhashitem',
  'pamhc2foodextended:cornedbeefitem',
  'pamhc2foodextended:guisoitem',
  'pamhc2foodextended:gourmetbeefburgeritem',
  'pamhc2foodextended:gourmetmuttonburgeritem',
  'pamhc2foodextended:hotandsoursoupitem',
  'pamhc2foodextended:jambalayaitem',
  'pamhc2foodextended:kohlundpinkelitem',
  'pamhc2foodextended:kungpaochickenitem',
  'pamhc2foodextended:meesuaitem',
  'pamhc2foodextended:paneertikkamasalaitem',
  'pamhc2foodextended:paradiseburgeritem',
  'pamhc2foodextended:porklomeinitem',
  'pamhc2foodextended:rainbowcurryitem',
  'pamhc2foodextended:swedishmeatballsitem',
  'pamhc2foodextended:szechuaneggplantitem'
]

function foodStationIntermediatePath(recipeId) {
  return `food_unification_station_${String(recipeId).replace(/[:\/.]/g, '_')}`
}

function foodStationIntermediateName(recipeId) {
  var path = String(recipeId).substring(String(recipeId).indexOf(':') + 1)
  var leaf = path.substring(path.lastIndexOf('/') + 1).replace(/item$/, '')
  return leaf
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.substring(1))
    .join(' ')
}

StartupEvents.registry('item', event => {
  FOOD_STAGED_STATION_RECIPE_IDS.forEach(recipeId => {
    event.create(foodStationIntermediatePath(recipeId))
      .displayName(`Prepared ${foodStationIntermediateName(recipeId)} Base`)
      .maxStackSize(16)
      .texture('minecraft:item/bowl')
  })
})
