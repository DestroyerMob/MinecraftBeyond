ServerEvents.recipes(event => {
  const armorMaterials = ['leather', 'iron', 'golden', 'diamond', 'netherite']
  const armorSlots = ['helmet', 'chestplate', 'leggings', 'boots']
  const moreWeaponsMaterials = ['wooden', 'stone', 'copper', 'iron', 'golden', 'diamond', 'netherite']
  const moreWeaponsTypes = ['battle_axe', 'great_sword', 'katana', 'knife', 'machete', 'spear']

  armorMaterials.forEach(material => {
    armorSlots.forEach(slot => {
      event.remove({ output: `minecraft:${material}_${slot}` })
    })
  })

  moreWeaponsMaterials.forEach(material => {
    moreWeaponsTypes.forEach(type => {
      event.remove({ output: `mobsmoreweapons:${material}_${type}` })
    })
  })
})
