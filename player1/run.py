import battlecode as bc
import random
import sys
import traceback
import os

PARAM_TEXT = '1000,1000,1000'    #initialize to default parameters
try:
    with open('params.txt','r') as fin:
        PARAM_TEXT = fin.readline()
except:
    pass
FACTORY_CAP,ROBOT_CAP,KNIGHT_RATIO = PARAM_TEXT.split(',')
FACTORY_CAP = int(FACTORY_CAP)
ROBOT_CAP = int(ROBOT_CAP)
KNIGHT_RATIO = float(KNIGHT_RATIO)
print('FACTORY_CAP=' + str(FACTORY_CAP))
print("ROBOT_CAP =" + str(ROBOT_CAP))
print('KNIGHT_RATIO=' + str(KNIGHT_RATIO))
LOW_WORKER_THRESHOLD = 10
REPLICATE_FIRST = True

def tryMove3(gc,unitID,dir):
    if dir == bc.Direction.Center or gc.can_move(unitID,dir):
        return dir
    if gc.can_move(unitID,dir.rotate_left()):
        return dir.rotate_left()
    return dir.rotate_right()

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()
print('$START_LOGGING\nparameters:' + PARAM_TEXT)
print('roundNum,karbonite,numFactories,numWorkers,numKnights')
while True:
    try:
        allMyUnits = gc.my_units()
        factories = [x for x in allMyUnits if x.unit_type == bc.UnitType.Factory]
        workers   = [x for x in allMyUnits if x.unit_type == bc.UnitType.Worker]
        knights   = [x for x in allMyUnits if x.unit_type == bc.UnitType.Knight]
        totalRobotsOnTeam = len(knights) + len(workers)
        if totalRobotsOnTeam == 0:
            totalRobotsOnTeam += 1
        visibleEnemies = {}

        # loop through factories
        for factory in factories:
            garrison = factory.structure_garrison()
            if len(garrison) > 0:
                for d in directions:
                    if gc.can_unload(factory.id,d):
                        gc.unload(factory.id,d)
                        break
            if totalRobotsOnTeam < ROBOT_CAP:
                nextRobotType = bc.UnitType.Worker
                if len(knights) < ROBOT_CAP * KNIGHT_RATIO:
                    nextRobotType = bc.UnitType.Knight
                if gc.can_produce_robot(factory.id, nextRobotType):
                    gc.produce_robot(factory.id, nextRobotType)

        # loop through workers
        for worker in workers:
            if not worker.location.is_on_map():
                continue
            hasKarbon = False
            # actions available to workers:
                # see
                # move
                # harvest   - if you can, do it in the first free direction
                # blueprint
                # build
                # repair
                # replicate - if you can, do it in the first free direction

            # Harvest - if you can harvest, do it in the first free direction
            for d in directions:
                if gc.can_harvest(worker.id, d):
                    gc.harvest(worker.id, d)
                    hasKarbon = True
                    break
                else:
                    hasKarbon = False

            #Replicate - if you can, do it in the first free direction
            if gc.karbonite() < 130 and len(factories) < FACTORY_CAP:
                pass
            elif len(workers) < ROBOT_CAP * (1 - KNIGHT_RATIO):
                for d in directions:
                    # if replicate heat too high, or resources too low, break
                    if gc.can_replicate(worker.id, d):
                        gc.replicate(worker.id, d)
                        break

            # Blueprint
            if len(factories) < FACTORY_CAP:
                for d in directions:
                    if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(worker.id,bc.UnitType.Factory, d):
                        gc.blueprint(worker.id, bc.UnitType.Factory, d)
                        break

            # repeat for build & repair
            neighbors = gc.sense_nearby_units_by_team(worker.location.map_location(),2,my_team)
            for neighbor in neighbors:
                if gc.can_build(worker.id, neighbor.id):
                    gc.build(worker.id, neighbor.id)
                elif gc.can_repair(worker.id, neighbor.id):
                    gc.repair(worker.id, neighbor.id)
            #move - if blueprinted in range, build. if factory < 50% -> repair, else move towards resources
            neighbors = gc.sense_nearby_units_by_team(worker.location.map_location(),50,my_team)
            d =  random.choice(directions)
            shouldMove = not hasKarbon
            for neighbor in neighbors:
                if gc.can_build(worker.id,neighbor.id):
                    d = worker.location.map_location().direction_to(neighbor.location.map_location())
                    shouldMove = True
                    break
                elif neighbor.health < 150:
                    d = worker.location.map_location().direction_to(neighbor.location.map_location())
                    shouldMove = True
                    break
            d = tryMove3(gc,worker.id,d)
            if shouldMove and gc.is_move_ready(worker.id) and gc.can_move(worker.id, d):
                gc.move_robot(worker.id, d)

            temp = gc.sense_nearby_units(worker.location.map_location(),50)
            enemies = [x for x in temp if x.team != my_team]
            for e in enemies:
                if e.id not in visibleEnemies.keys():
                    visibleEnemies[e.id] = e


        # loop through knights
        for knight in knights:
            if not knight.location.is_on_map():
                continue
            # knights can:
            # move, melee, javelin(must unlock)
            # if you can melee - do that (someone is close, and melee has less cooldown)
            # otherwise, move towards enemy then try to melee, finally, javelin if you can
            myLoc = knight.location.map_location()
            visibleUnits = gc.sense_nearby_units(myLoc,knight.vision_range)
            targets = [x for x in visibleUnits if x.team != my_team]
            closestEnemy = [None,None]
            meleed = False
            targetDir = None
            for target in targets:
                if target.id not in visibleEnemies.keys():
                    visibleEnemies[target.id] = target
                targetLoc = target.location.map_location()
                if myLoc.is_adjacent_to(targetLoc) and gc.is_attack_ready(knight.id) and gc.can_attack(knight.id, target.id):
                    gc.attack(knight.id, target.id)
                    meleed = True
                    break
                elif closestEnemy[1] == None:
                    closestEnemy = [target,myLoc.distance_squared_to(targetLoc)]
                    targetDir = myLoc.direction_to(targetLoc)
                elif myLoc.distance_squared_to(targetLoc) < closestEnemy[1]:
                    closestEnemy = [target, myLoc.distance_squared_to(targetLoc)]
                    targetDir = myLoc.direction_to(targetLoc)
            for enemy in visibleEnemies.values():
                enemyLoc = enemy.location.map_location()
                if closestEnemy[1] == None:
                    closestEnemy = [enemy,myLoc.distance_squared_to(enemyLoc)]
                    targetDir = myLoc.direction_to(enemyLoc)
                elif myLoc.distance_squared_to(enemyLoc) < closestEnemy[1]:
                    closestEnemy = [enemy,myLoc.distance_squared_to(enemyLoc)]
                    targetDir = myLoc.direction_to(enemyLoc)
            if not meleed and closestEnemy[1] != None:
                targetDir = tryMove3(gc, knight.id, targetDir)
                if gc.is_move_ready(knight.id) and gc.can_move(knight.id, targetDir):
                    gc.move_robot(knight.id, targetDir)
            elif not meleed and closestEnemy[1] == None:
                d = tryMove3(gc,knight.id,random.choice(directions))
                if gc.is_move_ready(knight.id) and gc.can_move(knight.id, d):
                    gc.move_robot(knight.id, d)
            if not meleed and closestEnemy[1] != None and gc.can_attack(knight.id,closestEnemy[0].id) and gc.is_attack_ready(knight.id):
                gc.attack(knight.id,closestEnemy[0].id)

        print(gc.round(), end=',')
        print(gc.karbonite(), end=',')
        print(len(factories), end=',')
        print(len(workers), end=',')
        print(len(knights), end='')
        print('\n')
    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()

# while True:
#     # We only support Python 3, which means brackets around print()
#     print('pyround:', gc.round())
#
#     # frequent try/catches are a good idea
#     try:
#         # walk through our units:
#         for unit in gc.my_units():
#
#             # first, factory logic
#             if unit.unit_type == bc.UnitType.Factory:
#                 garrison = unit.structure_garrison()
#                 if len(garrison) > 0:
#                     d = random.choice(directions)
#                     if gc.can_unload(unit.id, d):
#                         print('unloaded a knight!')
#                         gc.unload(unit.id, d)
#                         continue
#                 elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
#                     gc.produce_robot(unit.id, bc.UnitType.Knight)
#                     print('produced a knight!')
#                     continue
#
#             # first, let's look for nearby blueprints to work on
#             location = unit.location
#             if location.is_on_map():
#                 nearby = gc.sense_nearby_units(location.map_location(), 2)
#                 for other in nearby:
#                     if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
#                         gc.build(unit.id, other.id)
#                         print('built a factory!')
#                         # move onto the next unit
#                         continue
#                     if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
#                         print('attacked a thing!')
#                         gc.attack(unit.id, other.id)
#                         continue
#
#             # okay, there weren't any dudes around
#             # pick a random direction:
#             d = random.choice(directions)
#
#             # or, try to build a factory:
#             if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
#                 gc.blueprint(unit.id, bc.UnitType.Factory, d)
#             # and if that fails, try to move
#             elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
#                 gc.move_robot(unit.id, d)
#
#     except Exception as e:
#         print('Error:', e)
#         # use this to show where the error was
#         traceback.print_exc()
#
#     # send the actions we've performed, and wait for our next turn.
#     gc.next_turn()
#
#     # these lines are not strictly necessary, but it helps make the logs make more sense.
#     # it forces everything we've written this turn to be written to the manager.
#     sys.stdout.flush()
#     sys.stderr.flush()



# import battlecode as bc
# import random
# import sys
# import traceback
#
# import os
# print(os.getcwd())
#
# print("pystarting")
#
# # A GameController is the main type that you talk to the game with.
# # Its constructor will connect to a running game.
# gc = bc.GameController()
# directions = list(bc.Direction)
#
# print("pystarted")
#
# # It's a good idea to try to keep your bots deterministic, to make debugging easier.
# # determinism isn't required, but it means that the same things will happen in every thing you run,
# # aside from turns taking slightly different amounts of time due to noise.
# random.seed(6137)
#
# # let's start off with some research!
# # we can queue as much as we want.
# gc.queue_research(bc.UnitType.Rocket)
# gc.queue_research(bc.UnitType.Worker)
# gc.queue_research(bc.UnitType.Knight)
#
# my_team = gc.team()
#
# while True:
#     # We only support Python 3, which means brackets around print()
#     print('pyround:', gc.round())
#
#     # frequent try/catches are a good idea
#     try:
#         # walk through our units:
#         for unit in gc.my_units():
#
#             # first, factory logic
#             if unit.unit_type == bc.UnitType.Factory:
#                 garrison = unit.structure_garrison()
#                 if len(garrison) > 0:
#                     d = random.choice(directions)
#                     if gc.can_unload(unit.id, d):
#                         print('unloaded a knight!')
#                         gc.unload(unit.id, d)
#                         continue
#                 elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
#                     gc.produce_robot(unit.id, bc.UnitType.Knight)
#                     print('produced a knight!')
#                     continue
#
#             # first, let's look for nearby blueprints to work on
#             location = unit.location
#             if location.is_on_map():
#                 nearby = gc.sense_nearby_units(location.map_location(), 2)
#                 for other in nearby:
#                     if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
#                         gc.build(unit.id, other.id)
#                         print('built a factory!')
#                         # move onto the next unit
#                         continue
#                     if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
#                         print('attacked a thing!')
#                         gc.attack(unit.id, other.id)
#                         continue
#
#             # okay, there weren't any dudes around
#             # pick a random direction:
#             d = random.choice(directions)
#
#             # or, try to build a factory:
#             if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
#                 gc.blueprint(unit.id, bc.UnitType.Factory, d)
#             # and if that fails, try to move
#             elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
#                 gc.move_robot(unit.id, d)
#
#     except Exception as e:
#         print('Error:', e)
#         # use this to show where the error was
#         traceback.print_exc()
#
#     # send the actions we've performed, and wait for our next turn.
#     gc.next_turn()
#
#     # these lines are not strictly necessary, but it helps make the logs make more sense.
#     # it forces everything we've written this turn to be written to the manager.
#     sys.stdout.flush()
#     sys.stderr.flush()