def get_n_substance(size):
    maze_lvl = num_unlocked(Unlocks.Mazes)
    if maze_lvl == 0:
        return size
    return size * (2 ** (maze_lvl - 1))

def solve_maze_step(current_dir):
    if move(current_dir):
        return current_dir
    
    dirs = [North, East, South, West]
    idx = 0
    for i in range(4):
        if dirs[i] == current_dir:
            idx = i
            break
            
    for i in range(1, 4):
        new_idx = (idx + i) % 4
        new_dir = dirs[new_idx]
        if move(new_dir):
            return new_dir
    return None

def check_afford(thing):
    cost = get_cost(thing)
    if cost is None:
        return False
    for itm, amt in cost.items():
        if num_items(itm) < amt:
            return False
    return True

def try_unlock():
    priority = [
        Unlocks.Speed,
        Unlocks.Multi_Trade,
        Unlocks.Cactus,
        Unlocks.Mazes,
        Unlocks.Dinosaur,
        Unlocks.Carrots,
        Unlocks.Pumpkins,
        Unlocks.Polyculture,
        Unlocks.Expand,
        Unlocks.Plant
    ]
    for u in priority:
        if check_afford(u):
            unlock(u)
            return

def smart_trade(item, amount=10):
    cost = get_cost(item)
    if cost is None:
        return
    
    needed = 0
    pay_item = Items.Hay
    
    for k, v in cost.items():
        pay_item = k
        needed = v * amount
        
    if num_items(pay_item) > needed:
        if num_unlocked(Unlocks.Multi_Trade):
            trade(item, amount)
        else:
            for i in range(amount):
                trade(item)

def manage_supplies():
    try_unlock()
    
    seeds = [
        Entities.Cactus, Entities.Sunflower, 
        Entities.Carrots, Entities.Dinosaur, 
        Entities.Bush, Entities.Tree, Entities.Pumpkin
    ]
    for s in seeds:
        smart_trade(s, 50)
        
    if num_items(Items.Fertilizer) < 100:
        smart_trade(Items.Fertilizer, 10)
    if num_items(Items.Empty_Tank) < 10:
        smart_trade(Items.Empty_Tank, 5)

def boost_crop(entity, size):
    if entity == Entities.Bush:
        ws = num_items(Items.Weird_Substance)
        req = get_n_substance(size)
        if ws >= req:
            use_item(Items.Weird_Substance, req)
            return True
            
    if entity in [Entities.Sunflower, Entities.Dinosaur, Entities.Cactus, Entities.Pumpkin]:
        if num_items(Items.Fertilizer) > 0:
            use_item(Items.Fertilizer)
            
    if get_water() < 0.6:
        if num_items(Items.Water_Tank) > 0:
            use_item(Items.Water_Tank)
    return False

def main():
    world_size = get_world_size()
    max_petals = 0
    target_sun_x = 0
    target_sun_y = 0
    broken_cactus = False
    
    tasks = dict()
    
    # 0=Farm, 1=PrepMaze, 2=RunMaze
    mode = 0 
    maze_dir = East

    while True:
        cycle_broken_cactus = False
        
        if mode == 2:
            current_type = get_entity_type()
            if current_type == Entities.Treasure:
                harvest()
                mode = 0
            elif current_type == Entities.Hedge:
                next_d = solve_maze_step(maze_dir)
                if next_d:
                    maze_dir = next_d
                else:
                    mode = 0
            else:
                mode = 0
            continue

        for y in range(world_size):
            for x in range(world_size):
                
                # SENSING
                ent = get_entity_type()
                
                if ent == Entities.Sunflower:
                    p = measure()
                    if p > max_petals:
                        max_petals = p
                        target_sun_x = x
                        target_sun_y = y
                
                if ent == Entities.Cactus:
                    if x < world_size - 1:
                        curr = measure()
                        move(East)
                        nei = measure()
                        move(West)
                        if curr > nei:
                            swap(East)
                            cycle_broken_cactus = True
                
                comp = get_companion()
                if comp:
                    tasks[(comp[1], comp[2])] = comp[0]
                
                # LOGIC EXECUTION
                
                # Task
                if (x, y) in tasks:
                    req = tasks.pop((x, y))
                    if can_harvest(): harvest()
                    if get_ground_type() == Grounds.Grassland: till()
                    if plant(req):
                        boost_crop(req, world_size)
                    manage_supplies()
                
                # Hay (Critical)
                elif num_items(Items.Hay) < 5000:
                    if can_harvest(): harvest()
                    if get_ground_type() == Grounds.Soil: till()
                    plant(Entities.Grass)
                
                # Power (Critical)
                elif num_items(Items.Power) < 5000:
                    if ent == Entities.Sunflower and x == target_sun_x and y == target_sun_y:
                        harvest()
                        plant(Entities.Sunflower)
                    elif ent != Entities.Sunflower:
                        if can_harvest(): harvest()
                        if get_ground_type() == Grounds.Grassland: till()
                        plant(Entities.Sunflower)
                        boost_crop(Entities.Sunflower, world_size)

                # Maze Prep (Priority)
                elif mode == 1:
                    if ent != Entities.Bush:
                        if can_harvest(): harvest()
                        if get_ground_type() == Grounds.Soil: till()
                        plant(Entities.Bush)
                    if x == world_size - 1 and y == world_size - 1:
                        if boost_crop(Entities.Bush, world_size):
                            mode = 2
                            maze_dir = East
                            break 

                # Wood
                elif num_items(Items.Wood) < 10000 or num_items(Items.Weird_Substance) < get_n_substance(world_size):
                    if can_harvest(): harvest()
                    if (x + y) % 2 == 0:
                        plant(Entities.Tree)
                    else:
                        if get_ground_type() == Grounds.Soil: till()
                        plant(Entities.Bush)
                        boost_crop(Entities.Bush, world_size)
                
                # Trigger Maze Phase
                elif mode == 0 and num_items(Items.Gold) < 20000:
                    req_ws = get_n_substance(world_size)
                    if num_items(Items.Weird_Substance) >= req_ws:
                        mode = 1
                    else:
                        # Fallback to filling weird substance logic (Wood block handles this)
                        pass
                
                # Bones/Dino
                elif num_items(Items.Bone) < 5000:
                    if can_harvest(): harvest()
                    if get_ground_type() == Grounds.Grassland: till()
                    plant(Entities.Dinosaur)
                    boost_crop(Entities.Dinosaur, world_size)

                # Carrots
                elif num_items(Items.Carrot) < 5000:
                    if can_harvest(): harvest()
                    if get_ground_type() == Grounds.Grassland: till()
                    plant(Entities.Carrots)
                
                # Cactus (Default/Sort)
                else:
                    if ent == Entities.Cactus and not broken_cactus:
                        harvest()
                        plant(Entities.Cactus)
                    elif ent != Entities.Cactus:
                        if can_harvest(): harvest()
                        if get_ground_type() == Grounds.Grassland: till()
                        plant(Entities.Cactus)
                        boost_crop(Entities.Cactus, world_size)

                manage_supplies()

                if mode != 2:
                    if x == world_size - 1:
                        move(North)
                    else:
                        move(East)
            
            if mode == 2:
                break

            if y == 0:
                broken_cactus = cycle_broken_cactus
                if not broken_cactus:
                    max_petals = 0
main()
