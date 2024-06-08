from endstone.event import (
    event_handler
)
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone import ColorFormat
from functools import partial
from time import sleep

class PlayerTP(Plugin):
    api_version = "0.4"

    commands = {
        "tpa": {
            "description": "Request a teleport to specified player.",
            "usages": ["/tpa [target: player]"],
            "permissions": ["playertp.command.tpa"],
        },
        "tpaccept": {
            "description": "Accept the requested player to teleport to you.",
            "usages": ["/tpaccept"],
            "aliases": ["tpacc"],
            "permissions": ["playertp.command.tpaccept"]
        },
        "tpdeny": {
            "description": "Deny the requested player to teleport to you.",
            "usages": ["/tpdeny"],
            "aliases": ["tpd"],
            "permissions": ["playertp.command.tpdeny"]
        },
        "tpcancel": {
            "description": "Cancel your current teleport request.",
            "usages": ["/tpcancel"],
            "aliases": ["tpc"],
            "permissions": ["playertp.command.tpcancel"]
        }
    }
    
    permissions = {
        "playertp.command": {
            "description": "Allow users to use all commands provided by this plugin.",
            "default": True,
            "children": {
                "playertp.command.tpa": True,
                "playertp.command.tpaccept": True,
                "playertp.command.tpdeny": True,
                "playertp.command.tpcancel": True,
            },
        },
        "playertp.command.tpa": {
            "description": "Allow users to use the /tpa command.",
            "default": True,
        },
        "playertp.command.tpaccept": {
            "description": "Allow users to use the /tpaccept command.",
            "default": True,
        },
        "playertp.command.tpdeny": {
            "description": "Allow users to use the /tpdeny command.",
            "default": True,
        },
        "playertp.command.tpcancel": {
            "description": "Allow users to use the /tpcancel command.",
            "default": True,
        },
    }
    def __init__(self, *args, **kwargs):
        self.player_tp_queue = []
        super().__init__(*args, **kwargs)
    
    def on_enable(self):
        self.save_default_config()
        self.logger.info("PlayerTP has been enabled!")
        self.register_events(self)
    
    def on_disable(self):
        self.logger.info("PlayerTP has been disabled!")
    
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        match command.name:
            case "tpa":
                if len(args) > 0:
                    req_player = sender.as_player()
                    if sender.name == args[0]:
                        sender.send_error_message("Teleporting to yourself is not allowed!")
                        return False
                    if any(queue['sender'] == req_player.name for queue in self.player_tp_queue):
                        sender.send_error_message("You already have a pending teleport request!\nUse /tpcancel to cancel your current teleport request.")
                        return False
                    for tp_player in self.server.online_players:
                        if tp_player.name == args[0]:
                            req_player.send_message(f"{ColorFormat.YELLOW}Requesting teleport to {args[0]}!")
                            tp_player.send_message(f"{ColorFormat.RED}You have {self.config['timeout_timer']} seconds to accept the teleport request from {ColorFormat.WHITE}{req_player.name}")
                            tp_player.send_message(f"{ColorFormat.YELLOW}Use /tpaccept to accept or /tpdeny to deny the teleport request.")
                            self.player_tp_queue.append({"sender": f"{req_player.name}", "to_sender": f"{tp_player.name}"})
                            p = partial(self.tp_timeout, req_player, tp_player) 
                            self.server.scheduler.run_task_later(self, p, 20 * self.config["timeout_timer"])
                else:
                    sender.send_error_message("No player input found.\nUsage: /tpa <player>")
            case "tpaccept":
                tp_player = sender.as_player()
                for player_queue in self.player_tp_queue:
                    if player_queue["to_sender"] == tp_player.name:
                        p = partial(self.tp_accepted, player_queue["sender"], tp_player, player_queue)
                        self.server.scheduler.run_task(self, p)
            case "tpdeny":
                tp_player = sender.as_player()
                for player_queue in self.player_tp_queue:
                    if player_queue["to_sender"] == tp_player.name:
                        p = partial(self.tp_denied, player_queue["sender"], tp_player, player_queue)
                        self.server.scheduler.run_task(self, p)
            case "tpcancel":
                req_player = sender.as_player()
                for player_queue in self.player_tp_queue:
                    if player_queue["sender"] == req_player.name:
                        self.player_tp_queue.remove(player_queue)
                        req_player.send_message(f"{ColorFormat.YELLOW}You have canceled your teleport request.")
        return True
        
    def tp_accepted(self, req_player, tp_player, player_queue) -> None:
        for player_sender in self.server.online_players:
            if player_sender.name == req_player:
                player_sender.send_message(f"{ColorFormat.WHITE}{tp_player.name} {ColorFormat.GREEN}has accepted your request.")
                self.player_tp_queue.remove(player_queue)
                self.server.dispatch_command(self.server.command_sender, f"tp {player_sender.name} {tp_player.name}")
                # player_sender.send_message(f"{ColorFormat.YELLOW}Teleporting in {self.config['tp_request_delay'] - i} seconds...")
        
    def tp_denied(self, req_player, tp_player, player_queue) -> None:
        for player_sender in self.server.online_players:
            if player_sender.name == req_player:
                player_sender.send_message(f"{ColorFormat.WHITE}{tp_player.name} {ColorFormat.GREEN} has denied your request.")
                self.player_tp_queue.remove(player_queue)
        
    def tp_timeout(self, req_player, tp_player) -> None:
        for player_queue in self.player_tp_queue:
            if player_queue["to_sender"] == tp_player.name:
                req_player.send_message(f"{ColorFormat.WHITE}{tp_player.name} {ColorFormat.GREEN} has ignored your request.")
                self.player_tp_queue.remove(player_queue)
    
        