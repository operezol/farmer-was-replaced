dirs = [East, South, West, North]
dirs_index = {East: 0, South: 1, West: 2, North: 3}
MAX_PETALS = 15
MIN_PETALS = 7
WATER_LEVEL_TARGET = 0.40
BONE_GOAL = 100000

GLOBAL_MODE = 0
GLOBAL_DIR_X = East
GLOBAL_STEPS_IN_ROW = 0
GLOBAL_ROWS_VISITED = 0
GLOBAL_DINOSAUR_ENABLED = False

def get_right_dir(dir):
    return dirs[(dirs_index[dir] + 1) % 4]

def get_left_dir(dir):
    return dirs[(dirs_index[dir] - 1) % 4]

def pass_args_to_function(function, arg1=None, arg2=None, arg3=None):
    if not arg1:
        def result_function():
            function()
    elif not arg2:
        def result_function():
            function(arg1)
    elif not arg3:
        def result_function():
            function(arg1, arg2)
    else:
        def result_function():
            function(arg1, arg2, arg3)
    return result_function

def try_unlock():
    priority = [
        Unlocks.Speed, Unlocks.Expand, Unlocks.Plant,
        Unlocks.Carrots, Unlocks.Pumpkins, Unlocks.Polyculture,
        Unlocks.Cactus, Unlocks.Dinosaurs
    ]
    for u in priority:
        unlock(u)

def apply_water(current_mode):
    if get_water() < WATER_LEVEL_TARGET:
        if num_items(Items.Water) > 0:
            use_item(Items.Water)

def boost_crop(entity):
    if entity in [Entities.Sunflower, Entities.Pumpkin, Entities.Cactus]:
        if num_items(Items.Fertilizer) > 0:
            use_item(Items.Fertilizer)

def plant_and_boost_unified(entity_to_plant):
    if get_ground_type() == Grounds.Grassland:
        till()
        
    if get_entity_type() != entity_to_plant:
        if plant(entity_to_plant):
             boost_crop(entity_to_plant)

def main():
    
    global GLOBAL_MODE
    global GLOBAL_DIR_X
    global GLOBAL_STEPS_IN_ROW
    global GLOBAL_ROWS_VISITED
    global GLOBAL_DINOSAUR_ENABLED
    
    while True:
        world_size = get_world_size()

        try_unlock()
        
        if GLOBAL_MODE in [0, 3, 4]:
            
            current_mode = GLOBAL_MODE

            if can_harvest():
                harvest()
            apply_water(current_mode)
            
            entity_to_plant = None
            if current_mode == 3:
                entity_to_plant = Entities.Pumpkin
            elif current_mode == 4:
                entity_to_plant = Entities.Cactus
            elif current_mode == 0:
                if (get_pos_x() + get_pos_y()) % 2 == 0:
                    entity_to_plant = Entities.Tree
                else:
                    entity_to_plant = Entities.Bush

            if entity_to_plant:
                plant_and_boost_unified(entity_to_plant)

            if GLOBAL_STEPS_IN_ROW < world_size:
                move(GLOBAL_DIR_X)
                GLOBAL_STEPS_IN_ROW += 1
                
            else:
                move(North)
                GLOBAL_STEPS_IN_ROW = 0
                GLOBAL_ROWS_VISITED += 1
                
                if GLOBAL_DIR_X == East:
                    GLOBAL_DIR_X = West
                else:
                    GLOBAL_DIR_X = East

            if GLOBAL_ROWS_VISITED >= world_size:
                
                GLOBAL_STEPS_IN_ROW = 0
                GLOBAL_ROWS_VISITED = 0
                GLOBAL_DIR_X = East
                
                if GLOBAL_MODE == 0: 
                    GLOBAL_MODE = 3
                elif GLOBAL_MODE == 3: 
                    GLOBAL_MODE = 4
                elif GLOBAL_MODE == 4: 
                    GLOBAL_MODE = 0
                
        else:
            GLOBAL_MODE = 0
            
clear()
main()
