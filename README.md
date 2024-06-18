# PlayerTP

Simple player teleportation with confirmation for survival Endstone servers.

## Requirements
- [Endstone 4.7 build or higher](https://github.com/EndstoneMC/endstone)

## Commands
`/tpa <player>`

Request a teleport to specified player.

`/tpaccept`

Accept a teleport request.

`/tpdeny`

Deny a teleport request.

`/tpcancel`

Cancel your current teleport request.

## Configuration

- timeout_timer
  
  Teleport request timeout if player hasn't responded the request. (Seconds)

## Features
- [x] Player teleport confirmation
- [x] Player request teleport timeout
- [ ] Player teleport delay after confirmation agreed
- [ ] Teleport and confirmation sounds?