
from pydantic import BaseModel


class Rule(BaseModel):
	id: int
	rule_number: str
	is_technical: bool
	is_ranking_point: bool
	description: str


rules = [
	[
		1,
		'G211',
		False,
		False,
		'A strategy clearly aimed at forcing the opponent ALLIANCE to violate a rule is not in the spirit of FIRST Robotics Competition and not allowed.',
	],
	[
		2,
		'G211',
		True,
		False,
		'A strategy clearly aimed at forcing the opponent ALLIANCE to violate a rule is not in the spirit of FIRST Robotics Competition and not allowed. TECH FOUL if REPEATED.',
	],
	[
		3,
		'G301',
		True,
		False,
		'A DRIVE TEAM member may not cause significant delays to the start of their MATCH.',
	],
	[
		4,
		'G401',
		False,
		False,
		'In AUTO, a DRIVE TEAM member staged behind a STARTING LINE may not contact anything in front of that STARTING LINE, unless for personal or equipment safety, to press the E-Stop or A-Stop, or granted permission by a Head REFEREE or FTA.',
	],
	[
		5,
		'G402',
		False,
		False,
		'In AUTO, a DRIVE TEAM member may not directly or indirectly interact with a ROBOT or an OPERATOR CONSOLE unless for personal safety, OPERATOR CONSOLE safety, or pressing an E-Stop or A-Stop.',
	],
	[
		6,
		'G403',
		True,
		False,
		'In AUTO, a ROBOT may not CONTROL more than 1 NOTE at a time, either directly or transitively through other objects.',
	],
	[
		7,
		'G404',
		True,
		False,
		'In AUTO, a ROBOT whose BUMPERS are completely outside their WING may not cause a NOTE to travel into or through their WING such that the NOTE enters the WING while not in contact with that ROBOT.',
	],
	[
		8,
		'G405',
		True,
		False,
		'In AUTO, a ROBOT whose BUMPERS are completely across the CENTER LINE (i.e. to the opposite side of the CENTER LINE from its ROBOT STARTING ZONE) may contact neither an opponent ROBOT nor a NOTE staged in the opponent’s WING (regardless of who initiates the contact).',
	],
	[
		9,
		'G406',
		True,
		False,
		'A ROBOT may not deliberately use a GAME PIECE in an attempt to ease or amplify the challenge associated with a FIELD element.',
	],
	[
		10,
		'G407',
		True,
		False,
		'A ROBOT may not intentionally eject a NOTE from the FIELD (either directly or by bouncing off a FIELD element or other ROBOT) other than through a SPEAKER or AMP.',
	],
	[
		11,
		'G408',
		True,
		False,
		'A ROBOT may not cause a HIGH NOTE to leave the FIELD (including through an AMP or SPEAKER), score on a MICROPHONE, or enter a TRAP.',
	],
	[
		12,
		'G409',
		False,
		False,
		'In TELEOP, a ROBOT may neither A. leave its SOURCE ZONE with CONTROL of more than 1 NOTE nor B. have greater-than-MOMENTARY CONTROL of more than 1 NOTE, either directly or transitively through other objects, while outside their SOURCE ZONE.',
	],
	[13, 'G410', True, False, 'Neither a ROBOT nor a HUMAN PLAYER may damage a GAME PIECE.'],
	[14, 'G412', False, False, 'BUMPERS must be in BUMPER ZONE.'],
	[
		15,
		'G413',
		False,
		False,
		'A ROBOT may not expand beyond either of the following limits: A. its height, as measured when it’s resting normally on a flat floor, may not exceed 4 ft. or B. it may not extend more than 1 ft. from its FRAME PERIMETER.',
	],
	[
		16,
		'G413',
		True,
		False,
		'A ROBOT may not expand beyond either of the following limits: A. its height, as measured when it’s resting normally on a flat floor, may not exceed 4 ft. or B. it may not extend more than 1 ft. from its FRAME PERIMETER. TECH FOUL if used for strategic benefit.',
	],
	[
		17,
		'G414',
		False,
		False,
		'A ROBOT with any part of its BUMPERS in their opponent’s WING may not cause a NOTE to travel into or through their WING.',
	],
	[
		18,
		'G414',
		True,
		False,
		'A ROBOT with any part of its BUMPERS in their opponent’s WING may not cause a NOTE to travel into or through their WING. TECH FOUL if REPEATED.',
	],
	[
		19,
		'G415',
		True,
		False,
		'A ROBOT may not damage an ARENA element. A ROBOT is prohibited from the following interactions with an ARENA element, except chain and a GAME PIECE: grabbing, grasping, attaching to, becoming entangled with, suspending from.',
	],
	[
		20,
		'G416',
		True,
		False,
		'A ROBOT may not reduce the working length of chain. Incidental actions such as minor twisting due to ROBOT imbalance or ROBOT-to-ROBOT interaction are not considered violations of this rule.',
	],
	[
		21,
		'G417',
		False,
		False,
		'A ROBOT may not use a COMPONENT outside its FRAME PERIMETER (except its BUMPERS) to initiate contact with an opponent ROBOT inside the vertical projection of that opponent ROBOT’S FRAME PERIMETER.',
	],
	[
		22,
		'G418',
		True,
		False,
		'A ROBOT may not damage or functionally impair an opponent ROBOT in either of the following ways: A. deliberately, as perceived by a REFEREE. B. regardless of intent, by initiating contact, either directly or transitively via a GAME PIECE CONTROLLED by the ROBOT, inside the vertical projection of an opponent ROBOT’S FRAME PERIMETER.',
	],
	[
		23,
		'G419',
		True,
		False,
		'A ROBOT may not deliberately, as perceived by a REFEREE, attach to, tip, or entangle with an opponent ROBOT.',
	],
	[24, 'G420', False, False, 'A ROBOT may not PIN an opponent’s ROBOT for more than 5 seconds.'],
	[
		25,
		'G420',
		True,
		False,
		'A ROBOT may not PIN an opponent’s ROBOT for more than 5 seconds. An additional TECH FOUL for every 5 seconds in which the situation is not corrected.',
	],
	[
		26,
		'G421',
		True,
		False,
		'2 or more ROBOTS that appear to a REFEREE to be working together may neither isolate nor close off any major element of MATCH play.',
	],
	[
		27,
		'G422',
		True,
		False,
		'Prior to the last 20 seconds of a MATCH, a ROBOT may not contact (either directly or transitively through a GAME PIECE CONTROLLED by either ROBOT and regardless of who initiates contact) an opponent ROBOT whose BUMPERS are in contact with their PODIUM.',
	],
	[
		28,
		'G423',
		True,
		False,
		'A ROBOT may not contact (either directly or transitively through a GAME PIECE CONTROLLED by either ROBOT and regardless of who initiates contact) an opponent ROBOT if any part of either ROBOT’S BUMPERS are in the opponent’s SOURCE ZONE or AMP ZONE.',
	],
	[
		29,
		'G424',
		True,
		True,
		'A ROBOT may not contact (either directly or transitively through a GAME PIECE CONTROLLED by either ROBOT and regardless of who initiates contact) an opponent ROBOT if either of the following criteria are met: A. the opponent ROBOT has any part of its BUMPERS in its STAGE ZONE and it is not in contact with the carpet or B. any part of either ROBOT’S BUMPERS are in the opponent’s STAGE ZONE during the last 20 seconds of the MATCH.',
	],
	[
		30,
		'G425',
		False,
		False,
		'A DRIVE TEAM member must remain in their designated area as follows: A. a DRIVER may not contact anything outside the area in which they started the MATCH (i.e. the ALLIANCE AREA or SOURCE AREA), B. a DRIVER must use the OPERATOR CONSOLE in the DRIVER STATION to which they are assigned, as indicated on the team sign, C. a HUMAN PLAYER may not contact anything outside the area in which they started the MATCH (i.e. the ALLIANCE AREA or SOURCE AREA), D. a COACH may not contact anything outside the ALLIANCE AREA or in front of their COACH LINE, and E. a TECHNICIAN may not contact anything outside their designated area.',
	],
	[
		31,
		'G426',
		True,
		False,
		'A ROBOT shall be operated only by the DRIVERS and/or HUMAN PLAYERS of that team. A COACH activating their E-Stop or A-Stop is the exception to this rule.',
	],
	[32, 'G427', False, False, 'A DRIVE TEAM member may not extend into the CHUTE.'],
	[
		33,
		'G428',
		True,
		False,
		'A DRIVE TEAM member may not deliberately use a GAME PIECE in an attempt to ease or amplify a challenge associated with a FIELD element.',
	],
	[34, 'G429', True, False, 'A NOTE may only be introduced to the FIELD through the SOURCE.'],
	[
		35,
		'G430',
		False,
		False,
		'A HIGH NOTE may only be entered on to the FIELD during the last 20 seconds of the MATCH by a HUMAN PLAYER in front of the COACH LINE.',
	],
]

rule_map = {}


def get_rule_by_id(id: int) -> Rule:
	return get_all_rules().get(id)


def get_all_rules() -> dict[int, Rule]:
	if rule_map == {}:
		for rule in rules:
			rule_map[rule[0]] = Rule(
				id=rule[0],
				rule_number=rule[1],
				is_technical=rule[2],
				is_ranking_point=rule[3],
				description=rule[4],
			)
	return rule_map
