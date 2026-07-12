ServerEvents.recipes(event => {
  // MTF owns direct equipment progression. Tags make this apply to vanilla,
  // Extra Gems, and any other mod that follows the standard equipment tags.
  const blockedEquipmentTags = [
    'minecraft:axes',
    'minecraft:hoes',
    'minecraft:pickaxes',
    'minecraft:shovels',
    'minecraft:swords',
    'minecraft:head_armor',
    'minecraft:chest_armor',
    'minecraft:leg_armor',
    'minecraft:foot_armor',
    'minecraft:enchantable/crossbow',
    'c:tools/knife',
    'farmersdelight:tools/knives'
  ]

  blockedEquipmentTags.forEach(tag => {
    event.remove({
      not: { mod: 'mobstoolforging' },
      output: `#${tag}`
    })
  })

  // More Weapons' recipes are all finished weapons. Its MTF parts and station
  // data are not Recipe Manager recipes, so removing this namespace is safe.
  event.remove({ mod: 'mobsmoreweapons' })
})
