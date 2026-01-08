dirs = [East, South, West, North]
dirs_index = {East: 0, South: 1, West: 2, North: 3}
MAX_PETALS = 15 
MIN_PETALS = 7 
WATER_LEVEL_TARGET = 0.40 
BONE_GOAL = 100000 

def get_right_dir(dir):
    return dirs[(dirs_index[dir] + 1) % 4]
def get_left_dir(dir):
    return dirs[(dirs_index[dir] - 1) % 4]

def pass_args_to_function(function, arg1=None, arg2=None, arg3=None):
    if not arg1:
        def result_function(): function()
    elif not arg2:
        def result_function(): function(arg1)
    elif not arg3:
        def result_function(): function(arg1, arg2)
    else:
        def result_function(): function(arg1, arg2, arg3)
    return result_function

def goto_naive(x_target, y_target):
    n = get_world_size()
    curX, curY = get_pos_x(), get_pos_y()
    
    dx = (x_target - curX) % n
    dirX = East if dx <= n // 2 else West
    steps_x = dx if dx <= n // 2 else n - dx

    dy = (y_target - curY) % n
    dirY = North if dy <= n // 2 else South
    steps_y = dy if dy <= n // 2 else n - dy

    while steps_x > 0 or steps_y > 0:
        if steps_x >= steps_y and steps_x > 0:
            move(dirX)
            steps_x -= 1
        elif steps_y > 0:
            move(dirY)
            steps_y -= 1

def try_unlock():
    priority = [
        Unlocks.Speed, Unlocks.Expand, Unlocks.Plant,
        Unlocks.Carrots, Unlocks.Pumpkin, Unlocks.Polyculture,
        Unlocks.Cactus, Unlocks.Dinosaur_Hat
    ]
    for u in priority:
        unlock(u)

def apply_water():
    if get_water() < WATER_LEVEL_TARGET:
        if num_items(Items.Water) > 0:
            use_item(Items.Water)

def boost_crop(entity):
    if entity in [Entities.Sunflower, Entities.Pumpkin, Entities.Cactus]:
        if num_items(Items.Fertilizer) > 0:
            use_item(Items.Fertilizer) 
            apply_water() 

def dinosaur_safe_move(direction):
    if can_move(direction):
        move(direction)
        return True
    else:
        change_hat(Hats.Carrot_Hat)
        change_hat(Hats.Dinosaur_Hat)
        return False
        
def dinosaur_mode():
    change_hat(Hats.Dinosaur_Hat)
    n = get_world_size()
    
    while num_items(Items.Bone) < BONE_GOAL:
        for x in range(n):
            target_y = n - 1 if x % 2 == 0 else 1
            
            while get_pos_y() != target_y:
                d = North if target_y > get_pos_y() else South
                dinosaur_safe_move(d)

            if x < n - 1:
                dinosaur_safe_move(East)
        
        goto_naive(0, 0)
        harvest()

def sunflower_worker_task(petals_level, row_start, row_end):
    n = get_world_size()
    
    for y in range(row_start, row_end):
        goto_naive(0, y)
        
        is_row_ready = True
        for x in range(n):
            if get_entity_type() == Entities.Sunflower:
                if measure() != petals_level:
                    is_row_ready = False
                    break 
            
            if x < n - 1: move(East)
            
        if is_row_ready:
            goto_naive(0, y) 
            harvest() 
            plant(Entities.Sunflower) 
            
    return petals_level

def plant_and_boost_unified(entity_to_plant):
    if get_ground_type() == Grounds.Grassland:
        till()
        
    if get_entity_type() != entity_to_plant:
        if plant(entity_to_plant):
             boost_crop(entity_to_plant)

def farming_mode(current_mode):
    world_size = get_world_size()
    
    for y in range(world_size):
        for x in range(world_size):
            
            if can_harvest(): harvest()
            apply_water()
            
            if current_mode == 3:
                plant_and_boost_unified(Entities.Pumpkin)
            
            elif current_mode == 4:
                plant_and_boost_unified(Entities.Cactus)
            
            elif current_mode == 5:
                plant_and_boost_unified(Entities.Sunflower)
                        
            elif current_mode == 0:
                if (get_pos_x() + get_pos_y()) % 2 == 0:
                    plant_and_boost_unified(Entities.Tree)
                else:
                    plant_and_boost_unified(Entities.Bush)
                
            if x < world_size - 1: move(East)
        
        if y < world_size - 1: move(North)
        
    goto_naive(0, 0)

def main():
    
    mode = 0
    dinosaur_enabled = False 
    
    while True:
        world_size = get_world_size()
        
        try_unlock()
        
        if num_unlocked(Hats.Dinosaur_Hat) > 0 and not dinosaur_enabled:
            if num_items(Items.Egg) > 0:
                mode = 6 
                dinosaur_enabled = True
        
        if mode == 6:
            dinosaur_mode() 
            mode = 5 
            continue
            
        if mode == 5:
            n = get_world_size()
            row_division = n // 2 
            
            for p in range(MAX_PETALS, MIN_PETALS - 1, -1):
                spawn_drone(pass_args_to_function(sunflower_worker_task, p, 0, row_division))
                spawn_drone(pass_args_to_function(sunflower_worker_task, p, row_division, n))
                
            mode = 0
            continue
            
        if mode in [0, 3, 4]:
            
            farming_mode(mode)
            
            if mode == 0: mode = 3 
            elif mode == 3: mode = 4 
            elif mode == 4: mode = 5 
            
            continue 
            
        else:
            mode = 0
            
clear()
main()
