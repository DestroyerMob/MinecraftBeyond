ServerEvents.recipes(event => {
  event.shapeless(Item.of('minecraft:flint', 2), [
    'minecraft:gravel',
    'minecraft:gravel',
    'minecraft:gravel'
  ]).id('minecraft_beyond:gravel_to_flint')
})
