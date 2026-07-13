// Minecraft Beyond food integration policy
//
// Almost Unified selects canonical items before this event runs. This script
// then removes lower-priority ways of making those items and routes the food
// mods through one consistent set of kitchen stations.

var FOOD_UNIFICATION_TAG_PREFIX = 'minecraft_beyond:food_unification/'

// A few compatibility recipes use common tags that are empty in this exact
// mod set. Resolve them to the pack's preferred concrete ingredient before
// rebuilding the recipe so KubeJS never emits an invalid ingredient.
var FOOD_EMPTY_TAG_TARGETS = {
  'c:butters': 'farm_and_charm:butter',
  'c:cinnamon': 'expandeddelight:cinnamon',
  'c:flour': 'bountifulfares:flour',
  'c:oats': 'farm_and_charm:oat',
  'c:rhubarb': 'croptopia:rhubarb',
  'c:salts': 'expandeddelight:salt',
  'c:sliced_potato': 'moredelight:diced_potatoes',
  'c:vegetables/onion': 'farmersdelight:onion'
}

var FOOD_NAMESPACE_RANKS = {
  minecraft: 0,
  bountifulfares: 10,
  farmersdelight: 20,
  brewinandchewin: 21,
  crabbersdelight: 22,
  culturaldelights: 23,
  culturalrecipes: 23,
  ends_delight: 24,
  expandeddelight: 25,
  moredelight: 26,
  mynethersdelight: 27,
  oceansdelight: 28,
  bakery: 30,
  beachparty: 31,
  cornexpansion: 32,
  brewery: 33,
  candlelight: 34,
  farm_and_charm: 35,
  herbalbrews: 36,
  meadow: 37,
  naturalist: 38,
  spawn: 39,
  supplementaries: 40,
  vinery: 41,
  wildernature: 42,
  // Farmer's Croptopia is a method adapter, so its Farmer's Delight station
  // recipes beat Croptopia's legacy crafting-tool versions of the same food.
  farmerscroptopia: 49,
  croptopia: 50,
  pamhc2crops: 60,
  pamhc2foodcore: 61,
  pamhc2foodextended: 62,
  pamhc2trees: 63
}

var FOOD_PAM_NAMESPACES = new Set([
  'pamhc2crops',
  'pamhc2foodcore',
  'pamhc2foodextended'
])

// These namespaces belong to actual source mods rather than shared adapter
// namespaces. Once their output is canonicalized to a higher-priority mod,
// their lower-priority recipe is redundant even if an optional compatibility
// recipe was filtered before KubeJS could see it.
var FOOD_STRICT_RECIPE_NAMESPACES = new Set([
  'bountifulfares',
  'farmersdelight',
  'brewinandchewin',
  'crabbersdelight',
  'culturaldelights',
  'ends_delight',
  'expandeddelight',
  'moredelight',
  'mynethersdelight',
  'oceansdelight',
  'bakery',
  'beachparty',
  'cornexpansion',
  'brewery',
  'candlelight',
  'herbalbrews',
  'meadow',
  'naturalist',
  'spawn',
  'supplementaries',
  'vinery',
  'wildernature',
  'croptopia',
  'pamhc2crops',
  'pamhc2foodcore',
  'pamhc2foodextended',
  'pamhc2trees'
])

var FOOD_PAM_TOOL_TAGS = new Set([
  'c:tool_bakeware',
  'c:tool_cuttingboard',
  'c:tool_grinder',
  'c:tool_juicer',
  'c:tool_mixingbowl',
  'c:tool_pot',
  'c:tool_roller',
  'c:tool_saucepan',
  'c:tool_skillet'
])

var FOOD_OBSOLETE_KITCHEN_ITEMS = [
  'croptopia:cooking_pot',
  'croptopia:food_press',
  'croptopia:frying_pan',
  'croptopia:knife',
  'croptopia:mortar_and_pestle',
  'farm_and_charm:cooking_pot',
  'pamhc2foodcore:bakewareitem',
  'pamhc2foodcore:cuttingboarditem',
  'pamhc2foodcore:grinderitem',
  'pamhc2foodcore:juiceritem',
  'pamhc2foodcore:mixingbowlitem',
  'pamhc2foodcore:potitem',
  'pamhc2foodcore:rolleritem',
  'pamhc2foodcore:saucepanitem',
  'pamhc2foodcore:skilletitem'
]

// Bakery registers its oven recipes in Farm & Charm's namespace. These are
// the true baked goods from that set; its two grilled sandwiches stay on the
// stove because they are dry-cooked rather than baked.
var FOOD_BAKERY_BAKING_RECIPE_IDS = new Set([
  'farm_and_charm:stove/apple_pie',
  'farm_and_charm:stove/baguette',
  'farm_and_charm:stove/braided_bread',
  'farm_and_charm:stove/bread',
  'farm_and_charm:stove/bun',
  'farm_and_charm:stove/bundt_cake',
  'farm_and_charm:stove/chocolate_tart',
  'farm_and_charm:stove/cornet',
  'farm_and_charm:stove/croissant',
  'farm_and_charm:stove/crusty_bread',
  'farm_and_charm:stove/glowberry_tart',
  'farm_and_charm:stove/improved_bread',
  'farm_and_charm:stove/jam_roll',
  'farm_and_charm:stove/linzer_tart',
  'farm_and_charm:stove/misslilitu_biscuit',
  'farm_and_charm:stove/toast',
  'farm_and_charm:stove/waffle'
])

// Audited direct baked-food recipes. Display blocks, tools, slice reassembly,
// fried dough, griddle foods, and optional missing outputs are intentionally
// excluded instead of relying on broad output-name matching.
var FOOD_NATIVE_BAKING_RECIPE_IDS = new Set([
  'bountifulfares:apple_pie',
  'bountifulfares:artisan_bread',
  'bountifulfares:artisan_cookie',
  'bountifulfares:cocoa_cake',
  'bountifulfares:coconut_cake',
  'bountifulfares:elderberry_tart',
  'bountifulfares:glow_berry_tart',
  'bountifulfares:hoary_pie',
  'bountifulfares:lapisberry_tart',
  'bountifulfares:lemon_pie',
  'bountifulfares:maize_bread',
  'bountifulfares:melon_pie',
  'bountifulfares:orange_pie',
  'bountifulfares:passion_fruit_tart',
  'bountifulfares:plum_pie',
  'bountifulfares:sponge_cake',
  'bountifulfares:sweet_berry_tart',
  'bountifulfares:walnut_cookie',
  'brewinandchewin:pizza',
  'brewinandchewin:quiche_from_bacon',
  'brewinandchewin:quiche_from_mushroom',
  'ends_delight:food/chorus_cookie',
  'ends_delight:food/chorus_flower_pie',
  'ends_delight:food/chorus_fruit_pie',
  'expandeddelight:berry_sweet_roll',
  'expandeddelight:chocolate_cookie',
  'expandeddelight:cranberry_cobbler',
  'expandeddelight:glow_berry_sweet_roll',
  'expandeddelight:honeyed_goat_cheese_tart',
  'expandeddelight:sugar_cookie',
  'expandeddelight:sweet_roll',
  'farmersdelight:apple_pie',
  'farmersdelight:chocolate_pie',
  'farmersdelight:honey_cookie',
  'farmersdelight:shepherds_pie_block',
  'farmersdelight:sweet_berry_cheesecake',
  'farmersdelight:sweet_berry_cookie',
  'mynethersdelight:crafting/magma_cake',
  'mynethersdelight:crafting/striderloaf',
  'cornexpansion:corn_syrup_cookie',
  'meadow:cheese_tart',
  'meadow:cheesecake',
  'spawn:date_cookie',
  'croptopia:banana_nut_bread',
  'croptopia:corn_bread',
  'croptopia:meringue',
  'croptopia:nether_star_cake',
  'croptopia:nutty_cookie',
  'croptopia:pumpkin_bars',
  'croptopia:raisin_oatmeal_cookie',
  'croptopia:shaped_fruit_cake',
  'croptopia:shaped_lemon_coconut_bar',
  'croptopia:shaped_rhubarb_crisp',
  'croptopia:shaped_sticky_toffee_pudding',
  'croptopia:shaped_treacle_tart',
  'croptopia:snicker_doodle',
  'croptopia:tres_leche_cake'
])

var FOOD_LARGE_BAKING_RECIPE_IDS = new Set([
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
])

var FOOD_ASSEMBLY_RESULT_IDS = new Set([
  'croptopia:salsa',
  'pamhc2foodextended:bananasplititem',
  'pamhc2foodextended:berrymeringuenestitem',
  'pamhc2foodextended:fivespiceitem',
  'pamhc2foodextended:museliitem',
  'pamhc2foodextended:pokebowlitem',
  'pamhc2foodextended:springrollitem',
  'pamhc2foodextended:summersquashwithradishitem'
])

var FOOD_STAGED_STATION_RECIPE_IDS = new Set([
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
])

var FOOD_ROLLING_RECIPE_IDS = new Set([
  'farmerscroptopia:croptopia_cooking/noodle'
])

// Let's Do Compat includes these integrations even when their source add-ons
// are absent. They cannot deserialize in this pack and have no usable output,
// so remove them rather than carrying permanent recipe-load errors.
var FOOD_BROKEN_OPTIONAL_RECIPE_IDS = new Set([
  'letsdocompat:farmersdelight/farm_and_charm/pot_cooking/simple_tomato_soup',
  'letsdocompat:farm_and_charm/cooking/ghostly_chili'
])

// These recipes have an installed alternative that matches the pack's chosen
// method. Most are crafting alternatives to stations; sea salad is the inverse
// because every salad uses cold grid assembly. The two fugu conversions are
// removed because unification turns them into a canonical 1:3 duplication loop.
var FOOD_REDUNDANT_RECIPE_IDS = new Set([
  'bountifulfares:apple_stew',
  'bountifulfares:bountiful_stew',
  'bountifulfares:coconut_stew',
  'bountifulfares:fish_stew',
  'bountifulfares:leek_stew',
  'bountifulfares:cooking/sea_salad',
  'bountifulfares:stone_stew',
  'farmersdelight:melon_juice',
  'culturalrecipes:empanada',
  'culturalrecipes:tortilla_chips',
  'culturaldelights:tortilla_chips',
  'mynethersdelight:crafting/burnt_roll',
  'mynethersdelight:crafting/rock_soup',
  'spawn:clam_chowder',
  'spawn:clam_chowder_fd',
  'oceansdelight:crabbersdelight_pufferfish_conversion',
  'crabbersdelight:oceansdelight_fugu_conversion'
])

// These are intentionally the surviving station recipes for a higher-priority
// canonical output. Their native crafting alternatives are removed above, so
// strict namespace pruning must not remove the only coherent producer too.
var FOOD_STRICT_RECIPE_EXCEPTIONS = new Set([
  'expandeddelight:juicing/melon_juice',
  'farmersdelight:cooking/fish_stew',
  'meadow:cheese_form/cheese_wheel',
  'meadow:cheese_form/goat_cheese_wheel'
])

function foodNamespace(id) {
  var text = String(id)
  var separator = text.indexOf(':')
  return separator < 0 ? 'minecraft' : text.substring(0, separator)
}

function foodPath(id) {
  var text = String(id)
  var separator = text.indexOf(':')
  return separator < 0 ? text : text.substring(separator + 1)
}

function foodRank(id) {
  var text = String(id)
  // Callers deliberately pass both full resource IDs and an already-extracted
  // namespace. Treat a bare known namespace as such instead of as minecraft.
  var namespace = text.indexOf(':') < 0 ? text : foodNamespace(text)
  return Object.prototype.hasOwnProperty.call(FOOD_NAMESPACE_RANKS, namespace)
    ? FOOD_NAMESPACE_RANKS[namespace]
    : 1000
}

function foodParseRecipe(recipe) {
  try {
    return JSON.parse(String(recipe.json))
  } catch (error) {
    console.warn(`[Food Unification] Could not read ${String(recipe.getId())}: ${error}`)
    return null
  }
}

function foodResultInfo(value) {
  if (value == null) {
    return null
  }

  if (Array.isArray(value)) {
    return value.length > 0 ? foodResultInfo(value[0]) : null
  }

  if (typeof value === 'string') {
    return { id: value, count: 1 }
  }

  if (typeof value !== 'object') {
    return null
  }

  if (typeof value.id === 'string') {
    return { id: value.id, count: Number(value.count || 1) }
  }

  if (typeof value.item === 'string') {
    return { id: value.item, count: Number(value.count || 1) }
  }

  if (value.item != null) {
    var nested = foodResultInfo(value.item)
    if (nested != null && value.count != null) {
      nested.count = Number(value.count)
    }
    return nested
  }

  return null
}

function foodRecipeIngredients(json) {
  if (Array.isArray(json.ingredients)) {
    return json.ingredients.slice()
  }

  if (json.ingredient != null) {
    return [json.ingredient]
  }

  if (!Array.isArray(json.pattern) || json.key == null) {
    return []
  }

  var ingredients = []
  json.pattern.forEach(row => {
    String(row).split('').forEach(symbol => {
      if (symbol !== ' ' && json.key[symbol] != null) {
        ingredients.push(json.key[symbol])
      }
    })
  })
  return ingredients
}

function foodIngredientKey(ingredient) {
  if (ingredient == null) {
    return ''
  }

  if (typeof ingredient === 'string') {
    return ingredient.charAt(0) === '#' ? ingredient.substring(1) : ingredient
  }

  if (typeof ingredient.item === 'string') {
    return ingredient.item
  }

  if (typeof ingredient.tag === 'string') {
    return ingredient.tag
  }

  return ''
}

function foodIngredientMatches(ingredient, key) {
  if (ingredient == null) {
    return false
  }

  if (Array.isArray(ingredient)) {
    return ingredient.some(entry => foodIngredientMatches(entry, key))
  }

  return foodIngredientKey(ingredient) === key
}

function foodRemoveIngredient(ingredients, key) {
  return ingredients.filter(ingredient => !foodIngredientMatches(ingredient, key))
}

function foodPamToolTag(ingredients) {
  for (var ingredient of ingredients) {
    var key = foodIngredientKey(ingredient)
    if (FOOD_PAM_TOOL_TAGS.has(key)) {
      return key
    }
  }
  return null
}

function foodIngredientRetention(ingredient) {
  var key = foodIngredientKey(ingredient).toLowerCase()

  if (/dough|batter|flour|pasta|noodle|bread|tortilla/.test(key)) {
    return 0
  }

  if (/raw|cooked|meat|beef|pork|chicken|mutton|fish|egg|cheese|milk|cream|stock/.test(key)) {
    return 5
  }

  if (/crops\//.test(key) && !/spiceleaf|garlic|ginger|onion/.test(key)) {
    return 10
  }

  if (/fruit|vegetable|mushroom|nut|grain|rice|potato|carrot|tomato/.test(key)) {
    return 15
  }

  if (/sugar|honey|syrup|juice/.test(key)) {
    return 30
  }

  if (/salt|spice|pepper|oil|vinegar|condiment|dye|spiceleaf|garlic|ginger|onion/.test(key)) {
    return 100
  }

  return 20
}

function foodFitIngredients(ingredients, limit) {
  if (ingredients.length <= limit) {
    return ingredients.slice()
  }

  var seen = new Set()
  var uniqueIngredients = []
  var repeatedIngredients = []

  ingredients.forEach((ingredient, index) => {
    var key = foodIngredientKey(ingredient)
    if (key === '') key = JSON.stringify(ingredient)
    var entry = {
      ingredient: ingredient,
      index: index,
      retention: foodIngredientRetention(ingredient)
    }

    if (seen.has(key)) {
      repeatedIngredients.push(entry)
    } else {
      seen.add(key)
      uniqueIngredients.push(entry)
    }
  })

  var selected = uniqueIngredients
    .sort((left, right) => left.retention - right.retention || left.index - right.index)
    .slice(0, limit)

  if (selected.length < limit) {
    selected = selected.concat(
      repeatedIngredients
        .sort((left, right) => left.retention - right.retention || left.index - right.index)
        .slice(0, limit - selected.length)
    )
  }

  return selected
    .sort((left, right) => left.index - right.index)
    .map(entry => entry.ingredient)
}

function foodTakeContainer(ingredients, sourceJson) {
  if (sourceJson.container != null) {
    return {
      ingredients: ingredients,
      container: sourceJson.container
    }
  }

  for (var containerId of ['minecraft:bowl', 'minecraft:glass_bottle']) {
    var index = ingredients.findIndex(ingredient => foodIngredientMatches(ingredient, containerId))
    if (index >= 0) {
      var withoutContainer = ingredients.slice()
      withoutContainer.splice(index, 1)
      return {
        ingredients: withoutContainer,
        container: { id: containerId, count: 1 }
      }
    }
  }

  return { ingredients: ingredients, container: null }
}

function foodFdCookingJson(ingredients, result, sourceJson) {
  var prepared = foodTakeContainer(ingredients, sourceJson)
  var json = {
    type: 'farmersdelight:cooking',
    ingredients: foodFitIngredients(prepared.ingredients, 6),
    result: { id: result.id, count: result.count },
    experience: Number(sourceJson.experience || 0.5),
    recipe_book_tab: /juice|drink|cider|tea|coffee|soda|smoothie|milk/.test(foodPath(result.id))
      ? 'drinks'
      : 'meals'
  }

  if (prepared.container != null) {
    json.container = prepared.container
  }
  return json
}

function foodFdCuttingJson(ingredient, result) {
  return {
    type: 'farmersdelight:cutting',
    ingredients: [ingredient],
    tool: [
      { type: 'farmersdelight:item_ability', action: 'knife_dig' },
      { tag: 'c:tools/knife' }
    ],
    result: [
      { item: { id: result.id, count: result.count } }
    ]
  }
}

function foodBfMillingJson(ingredient, result) {
  return {
    type: 'bountifulfares:milling',
    ingredient: ingredient,
    result: { id: result.id },
    result_count: result.count
  }
}

function foodMincerJson(ingredient, result) {
  return {
    type: 'farm_and_charm:mincer',
    ingredient: ingredient,
    recipe_type: 'MEAT',
    result: { id: result.id, count: result.count }
  }
}

function foodJuicingJson(ingredients, result) {
  // The juicer declares its bottle separately. Croptopia press recipes often
  // include that bottle in the crafting ingredients, so remove it here rather
  // than charging players for both an input bottle and a container bottle.
  var preparedIngredients = foodRemoveIngredient(ingredients, 'minecraft:glass_bottle')
  return {
    type: 'expandeddelight:juicing',
    ingredients: foodFitIngredients(preparedIngredients, 2),
    container: { id: 'minecraft:glass_bottle', count: 1 },
    result: { id: result.id, count: result.count },
    experience: 0.35,
    recipe_book_tab: 'drinks'
  }
}

function foodStoveJson(ingredients, result, sourceJson) {
  return {
    type: 'farm_and_charm:stove',
    ingredients: foodFitIngredients(ingredients, 3),
    result: { id: result.id, count: result.count },
    experience: Number(sourceJson.experience || 0.35),
    requiresLearning: false
  }
}

function foodRoasterJson(ingredients, result) {
  return {
    type: 'farm_and_charm:roaster',
    ingredients: foodFitIngredients(ingredients, 6),
    container: { id: 'minecraft:bowl', count: 1 },
    result: { id: result.id, count: result.count },
    requiresLearning: false
  }
}

function foodMixingJson(ingredients, result) {
  return {
    type: 'farm_and_charm:crafting_bowl',
    ingredients: foodFitIngredients(ingredients, 4),
    result: { id: result.id, count: result.count }
  }
}

function foodAssemblyJson(ingredients, result) {
  return {
    type: 'minecraft:crafting_shapeless',
    ingredients: foodFitIngredients(ingredients, 9),
    result: { id: result.id, count: result.count }
  }
}

function foodAssemblyIngredients(ingredients, sourceJson) {
  var assembled = ingredients.slice()
  var container = foodResultInfo(sourceJson.container)
  if (container == null) return assembled

  for (var index = 0; index < container.count; index++) {
    assembled.push({ item: container.id })
  }
  return assembled
}

function foodMethodForPamTool(toolTag, result, ingredients) {
  var pamPath = foodPath(result.id)
  if (/salad/.test(pamPath)) return 'assembly'
  if (/deluxenachoes/.test(pamPath)) return 'baking'
  if (/pastagardenia/.test(pamPath)) return 'cooking'

  if (toolTag === 'c:tool_bakeware') return 'baking'
  if (toolTag === 'c:tool_cuttingboard') return ingredients.length === 1 ? 'cutting' : 'assembly'
  if (toolTag === 'c:tool_juicer') {
    var juicedPath = foodPath(result.id)
    if (/mayonnaise|mayonaise|hotsauce|hot_sauce|ketchup|relish|mustard|soysauce|soy_sauce|fruitpunch/.test(juicedPath)) {
      return 'mixing'
    }
    return 'juicing'
  }
  if (toolTag === 'c:tool_mixingbowl') return 'mixing'
  if (toolTag === 'c:tool_pot' || toolTag === 'c:tool_saucepan') {
    var cookedPath = foodPath(result.id)
    if (/peanutchocolatebar/.test(cookedPath)) return 'mixing'
    if (/chutney/.test(cookedPath)) return 'cooking'
    var usesCookingOil = ingredients.some(ingredient => foodIngredientMatches(ingredient, 'c:cookingoil'))
    if (usesCookingOil || /donut|doughnut|fries|chips|fritter|corndog|nugget|fried|hushpupp|mozzarella.*stick|porkrind|sesameball|zeppole|onionring|tempura|eggroll|batteredsausage/.test(cookedPath)) {
      return 'roaster'
    }
    return 'cooking'
  }
  if (toolTag === 'c:tool_roller') {
    var rolledPath = foodPath(result.id)
    if (/oil/.test(rolledPath)) return 'juicing'
    if (/pasta|noodle|tortilla/.test(rolledPath)) return 'rolling'
    return 'mixing'
  }
  if (toolTag === 'c:tool_skillet') return 'roaster'

  if (toolTag === 'c:tool_grinder') {
    if (ingredients.length === 1 && /ground(?:beef|chicken|fish|mutton|pork|rabbit|turkey|venison)|minced(?:beef|chicken|fish|mutton|pork|rabbit|turkey|venison)|pepperoni/.test(foodPath(result.id))) {
      return 'mincer'
    }
    return ingredients.length === 1 ? 'milling' : 'mixing'
  }

  return null
}

function foodMethodForCroptopiaTools(hasCookingPot, hasFoodPress, hasKnife, hasFryingPan, hasMortar, result, ingredients) {
  var path = foodPath(result.id)

  if (/salad/.test(path)) return 'assembly'

  if (hasFryingPan) {
    if (/pie|pizza|brownie|cinnamon_roll|scone|cornish_pasty|beef_wellington|quiche|baked_crepes/.test(path)) {
      return 'baking'
    }
    if (/goulash|ratatouille|steamed_clams|cabbage_roll|stuffed_artichoke|spaghetti_squash|refried_beans/.test(path)) {
      return 'cooking'
    }
    return 'roaster'
  }

  if (hasMortar) {
    return /paprika/.test(path) ? 'milling' : 'mixing'
  }

  if (hasKnife) {
    return ingredients.length === 1 ? 'cutting' : 'assembly'
  }

  if (hasFoodPress) {
    if (/ground_pork/.test(path)) return 'mincer'
    if (/macaron/.test(path)) return 'baking'
    if (/coffee/.test(path)) return 'cooking'
    if (/butter|beer|mead|wine|sauce/.test(path)) return 'mixing'
    return ingredients.length <= 2 ? 'juicing' : 'mixing'
  }

  if (hasCookingPot) {
    if (/dough|ice_cream|salad|butter/.test(path)) return 'mixing'
    if (path === 'noodle') return 'rolling'
    if (/fries|rings|chimichanga|relleno/.test(path)) return 'roaster'
    return 'cooking'
  }

  return null
}

function foodMethodForRecipeType(type) {
  if (type === 'farmersdelight:cooking') return 'cooking'
  if (type === 'farm_and_charm:pot_cooking') return 'cooking'
  if (type === 'farmersdelight:cutting') return 'cutting'
  if (type === 'bountifulfares:milling') return 'milling'
  if (type === 'expandeddelight:juicing') return 'juicing'
  if (type === 'farm_and_charm:crafting_bowl') return 'mixing'
  if (type === 'farm_and_charm:mincer') return 'mincer'
  if (type === 'farm_and_charm:roaster') return 'roaster'
  if (type === 'farm_and_charm:stove') return 'stove'
  return null
}

function foodGeneratedRecipeId(originalId) {
  return `minecraft_beyond:food_unification/${foodNamespace(originalId)}/${foodPath(originalId)}`
}

function foodBakingIntermediateId(originalId) {
  var safePath = `${foodNamespace(originalId)}_${foodPath(originalId)}`.replace(/[\/.]/g, '_')
  return `kubejs:food_unification_baking_${safePath}`
}

function foodStationIntermediateId(originalId) {
  var safePath = `${foodNamespace(originalId)}_${foodPath(originalId)}`.replace(/[\/.]/g, '_')
  return `kubejs:food_unification_station_${safePath}`
}

function foodKubeIngredient(ingredient) {
  if (typeof ingredient === 'string') {
    return ingredient
  }
  if (ingredient != null && typeof ingredient.item === 'string') {
    return ingredient.item
  }
  if (ingredient != null && typeof ingredient.tag === 'string') {
    return `#${ingredient.tag}`
  }
  return ingredient
}

function foodCustomTagTarget(tag) {
  if (typeof tag !== 'string' || !tag.startsWith(FOOD_UNIFICATION_TAG_PREFIX)) {
    return null
  }

  var generatedTargets = global.FOOD_UNIFICATION_TAG_TARGETS || {}
  if (Object.prototype.hasOwnProperty.call(generatedTargets, tag)) {
    var generatedTargetId = String(generatedTargets[tag])
    if (Item.exists(generatedTargetId)) return generatedTargetId
  }

  try {
    var target = AlmostUnified.getTagTargetItem(tag)
    var targetId = String(target.id)
    return targetId !== 'minecraft:air' && Item.exists(targetId) ? targetId : null
  } catch (error) {
    return null
  }
}

function foodCanonicalItemTarget(itemId) {
  var generatedTargets = global.FOOD_UNIFICATION_ITEM_TARGETS || {}
  if (!Object.prototype.hasOwnProperty.call(generatedTargets, itemId)) return itemId

  // Assets can exist for compatibility items that a mod did not register in
  // this installation. Never turn a valid source recipe into a ghost output.
  var targetId = String(generatedTargets[itemId])
  return Item.exists(targetId) ? targetId : itemId
}

function foodCanonicalIngredient(value) {
  if (value == null || typeof value === 'string') return value
  if (Array.isArray(value)) return value.map(foodCanonicalIngredient)

  if (typeof value === 'object') {
    if (typeof value.tag === 'string' &&
        Object.prototype.hasOwnProperty.call(FOOD_EMPTY_TAG_TARGETS, value.tag)) {
      var emptyTagTarget = FOOD_EMPTY_TAG_TARGETS[value.tag]
      if (Item.exists(emptyTagTarget)) return { item: emptyTagTarget }
    }

    var targetId = foodCustomTagTarget(value.tag)
    if (targetId != null) return { item: targetId }

    if (Array.isArray(value.children)) {
      value.children = value.children.map(foodCanonicalIngredient)
    }
    if (Array.isArray(value.ingredients)) {
      value.ingredients = value.ingredients.map(foodCanonicalIngredient)
    }
  }

  return value
}

function foodIngredientResolvable(value) {
  if (value == null) return true

  if (typeof value === 'string') {
    return value.startsWith('#') || Item.exists(value)
  }

  if (Array.isArray(value)) {
    return value.every(foodIngredientResolvable)
  }

  if (typeof value === 'object') {
    if (typeof value.tag === 'string' && value.tag.startsWith(FOOD_UNIFICATION_TAG_PREFIX)) {
      return foodCustomTagTarget(value.tag) != null
    }
    if (typeof value.item === 'string' && !Item.exists(value.item)) return false
    if (typeof value.id === 'string' && !Item.exists(value.id)) return false
    if (Array.isArray(value.children) && !value.children.every(foodIngredientResolvable)) return false
    if (Array.isArray(value.ingredients) && !value.ingredients.every(foodIngredientResolvable)) return false
  }

  return true
}

function foodIsUnificationItem(itemId) {
  // Broken optional-mod compatibility recipes can reference outputs that are not
  // registered in this pack. Avoid asking Item.of to resolve those ghost IDs.
  if (!Item.exists(itemId)) return false

  var generatedTargets = global.FOOD_UNIFICATION_ITEM_TARGETS || {}
  if (Object.prototype.hasOwnProperty.call(generatedTargets, itemId)) return true

  try {
    var tag = AlmostUnified.getRelevantItemTag(Item.of(itemId))
    return tag != null && String(tag).startsWith(FOOD_UNIFICATION_TAG_PREFIX)
  } catch (error) {
    return false
  }
}

ServerEvents.recipes(event => {
  var records = []
  var recordsByOutput = new Map()

  FOOD_BROKEN_OPTIONAL_RECIPE_IDS.forEach(id => event.remove({ id: id }))
  FOOD_REDUNDANT_RECIPE_IDS.forEach(id => event.remove({ id: id }))

  event.forEachRecipe({}, recipe => {
    var id = String(recipe.getId())
    if (FOOD_BROKEN_OPTIONAL_RECIPE_IDS.has(id) || FOOD_REDUNDANT_RECIPE_IDS.has(id)) {
      recipe.remove()
      return
    }

    var json = foodParseRecipe(recipe)
    if (json == null) return

    var result = foodResultInfo(json.result)
    var ingredients = foodRecipeIngredients(json)

    // Some broad compatibility datapacks ship recipes for optional mods that
    // are not installed. Leave those already-invalid recipes alone instead of
    // cloning them into the pack-owned namespace.
    if (result != null && !Item.exists(result.id)) return
    if (!foodIngredientResolvable(ingredients)) return
    if (!foodIngredientResolvable(json.container)) return

    if (result != null) result.id = foodCanonicalItemTarget(result.id)

    var record = {
      recipe: recipe,
      id: id,
      idNamespace: foodNamespace(id),
      json: json,
      type: String(json.type || ''),
      result: result,
      ingredients: ingredients,
      dropDuplicate: false,
      action: null
    }
    records.push(record)

    if (result != null) {
      if (!recordsByOutput.has(result.id)) recordsByOutput.set(result.id, [])
      recordsByOutput.get(result.id).push(record)
    }
  })

  // A lower-priority recipe is removed only when Almost Unified confirms the
  // output belongs to our food policy and a preferred/native recipe exists.
  records.forEach(record => {
    if (record.result == null || FOOD_STRICT_RECIPE_EXCEPTIONS.has(record.id) ||
        !foodIsUnificationItem(record.result.id)) return

    var recipeRank = foodRank(record.idNamespace)
    var outputRank = foodRank(record.result.id)
    if (recipeRank >= 1000 || recipeRank <= outputRank) return

    var alternatives = recordsByOutput.get(record.result.id) || []
    var hasPreferredRecipe = alternatives.some(alternative =>
      alternative !== record && foodRank(alternative.idNamespace) <= outputRank
    )
    record.dropDuplicate = hasPreferredRecipe || FOOD_STRICT_RECIPE_NAMESPACES.has(record.idNamespace)
  })

  var methodHints = new Map()
  records.forEach(record => {
    if (record.result == null || !FOOD_PAM_NAMESPACES.has(record.idNamespace)) return
    var toolTag = foodPamToolTag(record.ingredients)
    if (toolTag == null) return

    var ingredients = foodRemoveIngredient(record.ingredients, toolTag)
    var method = foodMethodForPamTool(toolTag, record.result, ingredients)
    if (method != null && !methodHints.has(record.result.id)) {
      methodHints.set(record.result.id, method)
    }
  })

  var stationMethods = new Map()
  records.forEach(record => {
    if (record.dropDuplicate || record.result == null) return
    var method = foodMethodForRecipeType(record.type)
    if (method == null) return
    if (!stationMethods.has(record.result.id)) stationMethods.set(record.result.id, new Set())
    stationMethods.get(record.result.id).add(method)
  })

  var counts = {
    duplicate: 0,
    obsolete: 0,
    cooking: 0,
    cutting: 0,
    milling: 0,
    mincer: 0,
    juicing: 0,
    stove: 0,
    roaster: 0,
    mixing: 0,
    assembly: 0,
    baking: 0,
    rolling: 0,
    alternate: 0
  }

  records.forEach(record => {
    if (record.dropDuplicate) {
      record.action = { kind: 'remove', reason: 'duplicate' }
      counts.duplicate++
      return
    }

    if (record.result != null && FOOD_OBSOLETE_KITCHEN_ITEMS.includes(record.result.id)) {
      record.action = { kind: 'remove', reason: 'obsolete' }
      counts.obsolete++
      return
    }

    if (record.result == null) return

    var method = null
    var ingredients = record.ingredients.map(foodCanonicalIngredient)

    if (/salad/.test(foodPath(record.result.id)) || FOOD_ASSEMBLY_RESULT_IDS.has(record.result.id)) {
      var saladToolTag = foodPamToolTag(ingredients)
      if (saladToolTag != null) ingredients = foodRemoveIngredient(ingredients, saladToolTag)
      for (var saladTool of [
        'croptopia:cooking_pot',
        'croptopia:food_press',
        'croptopia:frying_pan',
        'croptopia:knife',
        'croptopia:mortar_and_pestle'
      ]) {
        ingredients = foodRemoveIngredient(ingredients, saladTool)
      }
      if (record.result.id === 'pamhc2foodextended:pokebowlitem') {
        ingredients = ingredients.map(ingredient =>
          foodIngredientMatches(ingredient, 'c:crops/rice')
            ? { item: 'farmersdelight:cooked_rice' }
            : ingredient
        )
      }
      ingredients = foodAssemblyIngredients(ingredients, record.json)
      method = 'assembly'
    } else if (FOOD_BAKERY_BAKING_RECIPE_IDS.has(record.id) || FOOD_NATIVE_BAKING_RECIPE_IDS.has(record.id)) {
      method = 'baking'
    } else if (FOOD_ROLLING_RECIPE_IDS.has(record.id)) {
      method = 'rolling'
    } else if (record.type === 'farm_and_charm:pot_cooking') {
      method = 'cooking'
    } else if (FOOD_PAM_NAMESPACES.has(record.idNamespace)) {
      var toolTag = foodPamToolTag(ingredients)
      if (toolTag != null) {
        ingredients = foodRemoveIngredient(ingredients, toolTag)
        method = foodMethodForPamTool(toolTag, record.result, ingredients)
      }
    } else if ((record.idNamespace === 'croptopia' || record.idNamespace === 'farmerscroptopia') && /^minecraft:crafting_/.test(record.type)) {
      if (stationMethods.has(record.result.id) && stationMethods.get(record.result.id).size > 0) {
        record.action = { kind: 'remove', reason: 'alternate' }
        counts.alternate++
        return
      }

      var hasCookingPot = ingredients.some(ingredient => foodIngredientMatches(ingredient, 'croptopia:cooking_pot'))
      var hasFoodPress = ingredients.some(ingredient => foodIngredientMatches(ingredient, 'croptopia:food_press'))
      var hasKnife = ingredients.some(ingredient => foodIngredientMatches(ingredient, 'croptopia:knife'))
      var hasFryingPan = ingredients.some(ingredient => foodIngredientMatches(ingredient, 'croptopia:frying_pan'))
      var hasMortar = ingredients.some(ingredient => foodIngredientMatches(ingredient, 'croptopia:mortar_and_pestle'))

      if (hasCookingPot || hasFoodPress || hasKnife || hasFryingPan || hasMortar) {
        ingredients = foodRemoveIngredient(ingredients, 'croptopia:cooking_pot')
        ingredients = foodRemoveIngredient(ingredients, 'croptopia:food_press')
        ingredients = foodRemoveIngredient(ingredients, 'croptopia:knife')
        ingredients = foodRemoveIngredient(ingredients, 'croptopia:frying_pan')
        ingredients = foodRemoveIngredient(ingredients, 'croptopia:mortar_and_pestle')
        method = foodMethodForCroptopiaTools(
          hasCookingPot,
          hasFoodPress,
          hasKnife,
          hasFryingPan,
          hasMortar,
          record.result,
          ingredients
        )
      } else if (methodHints.has(record.result.id)) {
        method = methodHints.get(record.result.id)
      }
    }

    if (method == null) return

    var stagedStation = FOOD_STAGED_STATION_RECIPE_IDS.has(record.id) &&
      (method === 'cooking' || method === 'roaster') && ingredients.length > 6
    var customJson = null
    if (!stagedStation) {
      if (method === 'cooking') customJson = foodFdCookingJson(ingredients, record.result, record.json)
      if (method === 'cutting' && ingredients.length > 0) customJson = foodFdCuttingJson(ingredients[0], record.result)
      if (method === 'milling' && ingredients.length > 0) customJson = foodBfMillingJson(ingredients[0], record.result)
      if (method === 'mincer' && ingredients.length > 0) customJson = foodMincerJson(ingredients[0], record.result)
      if (method === 'juicing') customJson = foodJuicingJson(ingredients, record.result)
      if (method === 'stove') customJson = foodStoveJson(ingredients, record.result, record.json)
      if (method === 'roaster') customJson = foodRoasterJson(ingredients, record.result)
      if (method === 'mixing') customJson = foodMixingJson(ingredients, record.result)
      if (method === 'assembly') customJson = foodAssemblyJson(ingredients, record.result)
    }

    if (method === 'rolling') {
      record.action = {
        kind: method,
        ingredients: foodFitIngredients(ingredients, 8)
      }
    } else if (method === 'baking') {
      record.action = {
        kind: method,
        ingredients: ingredients.slice(),
        staged: FOOD_LARGE_BAKING_RECIPE_IDS.has(record.id)
      }
    } else if (stagedStation) {
      record.action = {
        kind: 'staged_station',
        method: method,
        ingredients: ingredients.slice(),
        sourceJson: record.json
      }
    } else if (customJson != null) {
      record.action = { kind: 'custom', json: customJson }
    }

    if (record.action != null) counts[method]++
  })

  // Remove originals first. Added recipes use pack-owned IDs so fallback/raw
  // serializers cannot collide with the recipes being replaced.
  records.forEach(record => {
    if (record.action != null) record.recipe.remove()
  })

  records.forEach(record => {
    if (record.action == null || record.action.kind === 'remove') return
    var generatedId = foodGeneratedRecipeId(record.id)

    if (record.action.kind === 'custom') {
      event.custom(record.action.json).id(generatedId)
      return
    }

    if (record.action.kind === 'staged_station') {
      var stationIntermediateId = foodStationIntermediateId(record.id)
      var stationPreparedIngredients = record.action.ingredients.slice(0, 4)
      var stationFinishingIngredients = record.action.ingredients.slice(4)
      event.custom(foodMixingJson(stationPreparedIngredients, { id: stationIntermediateId, count: 1 }))
        .id(`${generatedId}/prepare`)

      var stationIngredients = [{ item: stationIntermediateId }].concat(stationFinishingIngredients)
      var stationJson = record.action.method === 'cooking'
        ? foodFdCookingJson(stationIngredients, record.result, record.action.sourceJson)
        : foodRoasterJson(stationIngredients, record.result)
      event.custom(stationJson).id(generatedId)
      return
    }

    if (record.action.kind === 'rolling') {
      var inputs = record.action.ingredients.map(foodKubeIngredient)
      inputs.push('bakery:rolling_pin')
      event.shapeless(Item.of(record.result.id, record.result.count), inputs)
        .keepIngredient('bakery:rolling_pin')
        .id(generatedId)
      return
    }

    if (record.action.kind === 'baking') {
      var bakingIngredients = record.action.ingredients
      if (record.action.staged && bakingIngredients.length > 8) {
        var intermediateId = foodBakingIntermediateId(record.id)
        var preparedIngredients = bakingIngredients.slice(0, 4)
        var finishingIngredients = bakingIngredients.slice(4)
        event.custom(foodMixingJson(preparedIngredients, { id: intermediateId, count: 1 }))
          .id(`${generatedId}/prepare`)
        bakingIngredients = [{ item: intermediateId }].concat(finishingIngredients)
      }

      var inputs = foodFitIngredients(bakingIngredients, 8).map(foodKubeIngredient)
      inputs.push('bakery:tray')
      event.shapeless(Item.of(record.result.id, record.result.count), inputs)
        .keepIngredient('bakery:tray')
        .id(generatedId)
    }
  })

  console.info(
    '[Food Unification] ' +
    `duplicates=${counts.duplicate}, alternates=${counts.alternate}, obsolete=${counts.obsolete}, ` +
    `pot=${counts.cooking}, cutting=${counts.cutting}, milling=${counts.milling}, ` +
    `mincer=${counts.mincer}, juicing=${counts.juicing}, stove=${counts.stove}, ` +
    `roaster=${counts.roaster}, mixing=${counts.mixing}, assembly=${counts.assembly}, ` +
    `baking=${counts.baking}, rolling=${counts.rolling}`
  )
})

RecipeViewerEvents.removeEntriesCompletely('item', event => {
  FOOD_OBSOLETE_KITCHEN_ITEMS.forEach(item => event.remove(item))
})
