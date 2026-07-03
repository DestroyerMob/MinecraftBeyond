const PlayerWarpsCommands = Java.loadClass('net.minecraft.commands.Commands')
const PlayerWarpsStringArgumentType = Java.loadClass('com.mojang.brigadier.arguments.StringArgumentType')
const PlayerWarpsComponent = Java.loadClass('net.minecraft.network.chat.Component')
const PlayerWarpsFTBEWorldData = Java.loadClass('dev.ftb.mods.ftbessentials.util.FTBEWorldData')
const PlayerWarpsTeleportPos = Java.loadClass('dev.ftb.mods.ftbessentials.util.TeleportPos')

function playerWarpsName(rawName) {
  const name = String(rawName).trim().toLowerCase()

  if (name.length === 0) {
    return null
  }

  return name
}

function playerWarpsManager(source) {
  const worldData = PlayerWarpsFTBEWorldData.instance

  if (worldData == null) {
    source.sendFailure(PlayerWarpsComponent.literal('FTB Essentials warp data is not ready yet.'))
    return null
  }

  return worldData.warpManager()
}

function playerWarpsSet(context) {
  const source = context.getSource()
  const player = source.getPlayerOrException()
  const manager = playerWarpsManager(source)
  const name = playerWarpsName(PlayerWarpsStringArgumentType.getString(context, 'name'))

  if (manager == null) {
    return 0
  }

  if (name == null) {
    source.sendFailure(PlayerWarpsComponent.literal('Warp name cannot be blank.'))
    return 0
  }

  manager.addDestination(name, new PlayerWarpsTeleportPos(player), player)
  player.displayClientMessage(PlayerWarpsComponent.literal("Warp '" + name + "' set."), false)
  return 1
}

function playerWarpsDelete(context) {
  const source = context.getSource()
  const player = source.getPlayerOrException()
  const manager = playerWarpsManager(source)
  const name = playerWarpsName(PlayerWarpsStringArgumentType.getString(context, 'name'))

  if (manager == null) {
    return 0
  }

  if (name == null) {
    source.sendFailure(PlayerWarpsComponent.literal('Warp name cannot be blank.'))
    return 0
  }

  if (manager.deleteDestination(name)) {
    player.displayClientMessage(PlayerWarpsComponent.literal("Warp '" + name + "' deleted."), false)
    return 1
  }

  player.displayClientMessage(PlayerWarpsComponent.literal("Warp '" + name + "' was not found."), false)
  return 0
}

function playerWarpsRegister(event, commandName, action) {
  event.register(
    PlayerWarpsCommands.literal(commandName)
      .then(
        PlayerWarpsCommands.argument('name', PlayerWarpsStringArgumentType.greedyString())
          .executes(action)
      )
  )
}

ServerEvents.commandRegistry(event => {
  playerWarpsRegister(event, 'setwarp', playerWarpsSet)
  playerWarpsRegister(event, 'delwarp', playerWarpsDelete)
  playerWarpsRegister(event, 'playersetwarp', playerWarpsSet)
  playerWarpsRegister(event, 'playerdelwarp', playerWarpsDelete)
})
