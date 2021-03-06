import logging
from spock.mcmap import smpmap
from spock.mcp import mcdata, mcpacket
from spock.mcp.mcpacket import Packet
from spock.utils import pl_announce
from micropsi_core.world.minecraft.psidispatcher import PsiDispatcher, STANCE_ADDITION

STANCE_ADDITION = 1.620
STEP_LENGTH = 1.0
JUMPING_MAGIC_NUMBER = 0  # 2 used to work


@pl_announce('Micropsi')
class MicropsiPlugin(object):

    def __init__(self, ploader, settings):

        # register required plugins
        self.net = ploader.requires('Net')
        self.event = ploader.requires('Event')
        self.world = ploader.requires('World')
        self.clientinfo = ploader.requires('ClientInfo')
        self.threadpool = ploader.requires('ThreadPool')

        #
        self.event.reg_event_handler(
            'cl_position_update',
            self.subtract_stance
        )

        self.psi_dispatcher = PsiDispatcher(self)

        # make references between micropsi world and MicropsiPlugin
        self.micropsi_world = settings['micropsi_world']
        self.micropsi_world.spockplugin = self

    def chat(self, message):
        self.net.push(Packet(ident='PLAY>Chat Message', data={'message': message}))

    def dispatchMovement(self, bot_coords, current_section, move_x, move_z):
        target_coords = (self.normalize_coordinate(bot_coords[0] + (STEP_LENGTH if (move_x > 0) else 0) + (-STEP_LENGTH if (move_x < 0) else 0)),
                         bot_coords[1],
                         self.normalize_coordinate(bot_coords[2] + (STEP_LENGTH if (move_z > 0) else 0) + (-STEP_LENGTH if (move_z < 0) else 0)))

        target_block_coords = (self.normalize_block_coordinate(target_coords[0]),
                               self.normalize_block_coordinate(target_coords[1]),
                               self.normalize_block_coordinate(target_coords[2]))
        ground_offset = 0
        for y in range(0, 16):
            if current_section.get(target_block_coords[0], y, target_block_coords[2]).id != 0:
                ground_offset = y + 1
        if target_coords[1] // 16 * 16 + ground_offset - target_coords[1] <= 1:
            self.move(position={
                'x': target_coords[0],
                'y': target_coords[1] // 16 * 16 + ground_offset,
                'z': target_coords[2],
                'yaw': self.clientinfo.position['yaw'],
                'pitch': self.clientinfo.position['pitch'],
                'on_ground': self.clientinfo.position['on_ground'],
                'stance': target_coords[1] // 16 * 16 + ground_offset + STANCE_ADDITION
            })

    def move(self, position=None):

        if not (self.net.connected and self.net.proto_state == mcdata.PLAY_STATE):
            return
        # writes new data to clientinfo which is pulled and pushed to Minecraft by ClientInfoPlugin
        self.clientinfo.position = position

    def subtract_stance(self, name, packet):

        # this is to correctly calculate a y value -- the server seems to deliver the value with stance addition,
        # but for movements it will have to be sent without (the "foot" value).
        # Movements sent with stance addition (eye values sent as foot values) will be silently discarded
        # by the server as impossible, which is undesirable.
        self.clientinfo.position['stance'] = self.clientinfo.position['y']
        self.clientinfo.position['y'] = self.clientinfo.position['y'] - STANCE_ADDITION

    def normalize_coordinate(self, coordinate):
        return coordinate // 1 + 0.5

    def normalize_block_coordinate(self, coordinate):
        return int(coordinate // 1 % 16)
