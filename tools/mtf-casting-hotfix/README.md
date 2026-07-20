# MTF casting visual hotfix

This source targets the casting implementation in the deployed
`minecraft/mods/mobstoolforging-local.jar`.

The checked-out `minecraft/mod-dev/MobsToolForging` source predates the casting
classes contained in that jar, so these focused replacement classes are kept
separately until the newer MTF source snapshot is restored. The hotfix:

- installs the supplied full-height casting table and basin models;
- matches the table, basin, and faucet voxel shapes to their models;
- aligns cast contents and fluid surfaces with the new models; and
- positions the faucet stream at the channel outlet and terminates it at the
  receiver's live fluid level; and
- installs the supplied foundry-glass artwork as Fusion's five-tile `pieced`
  connected-texture layout.

`classpath.init.gradle` exposes the MTF development classpath used to compile
the replacement classes against the deployed jar.

The two supplied foundry-glass PNGs are retained unchanged in `source-assets`.
Run `generate-connected-texture.ps1` to assemble them into the deployable
80-by-16 pieced atlas without modifying their pixels.
