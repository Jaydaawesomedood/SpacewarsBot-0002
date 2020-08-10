# -*- coding: utf-8 -*-
import random, json, math, os, textwrap, sys
import facebook as fb
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

astros = pd.read_csv('data/astros.csv')
colors = ["#2bede7", "#ffda45", "#ea4fff", "#85ffad", "#ff96c5", "#96adff"]
cosmic_dew = {"color": "#ff4a53"}

crew_pic = [
    [],
    {'members_layout': {
        'x': 136,
        'y': [120,250,380,510],
        'size': 100,
        'name_x': 250,
        'statusbar_x': 300,
        'statusbar_ydiff': 35,
        'statusbar_w': 300,
        'statusbar_h': 8,
        'statusbar_space': 10
        },
      'extra_member': {
        'x': 18,
        'y': 640,
        'text_x': 90
        }
     },
    {'members_layout': {
        'x': [60,228,392,560],
        'y_attacker': 120,
        'y_target': 500,
        'size': 100,
        }
     }
    ]

def read_crew():
    with open('data/crew.json', 'r') as f:
        crews = json.load(f)
    return crews

def config_crews(obj):
    with open('data/crew.json', 'w') as f:
        json.dump(obj, f, indent = 4, ensure_ascii = False)

def read_astro():
    with open('data/astros.json', 'r') as f:
        represents = json.load(f)
    return represents

def config_astro(obj):
    with open('data/astros.json', 'w') as f:
        json.dump(obj, f, indent = 4, ensure_ascii = False)

def read_planets():
    with open('data/planets.json', 'r') as f:
        planets = json.load(f)
    return planets

def config_planets(obj):
    with open('data/planets.json', 'w') as f:
        json.dump(obj, f, indent = 3, ensure_ascii = False)
        
def read_last_post():
    with open('data/page_info.json', 'r') as f:
        page = json.load(f)
    return page

class pre_game():
    def __init__(self):
        crews = self.gen_crews(astros)
        all_astros = {}
        for astro in astros['rep_name']:
            astro_stats = {}
            astro_stats['strength'] = random.randint(20,100)
            astro_stats['hunger'] = 100
            astro_stats['thirst'] = 100
            astro_stats['sanity'] = 100
            astro_stats['status'] = 'Alive'
            all_astros[astro] = astro_stats
        
        config_astro(all_astros)
            
    def gen_crews(self, reps):
        crews = {}
        crew_count = 1
        while not(len(reps) == 0):
            ship_info = {}
            crew_members = []
            crew = reps.sample(n = 4)
            for index, member in crew.iterrows():
                crew_members.append(member['rep_name'])
                reps = reps.drop(index)
            
            ship_info['members'] = crew_members
            ship_info['food'] = 100
            ship_info['water'] = 100
            ship_info['oxygen'] = 100
            ship_info['pressure'] = 100
            ship_info['speed'] = random.randint(30,60)
            ship_info['weapon'] = {'attack' : random.randint(10,15), 'range': random.randint(30,50)}
            ship_info['radar'] = random.randint(80, 100)
            ship_info['position'] = ()
            ship_info['status'] = 'Active'
            
            
            crews['crew{}'.format(crew_count)] = ship_info
            crew_count += 1
        
        config_crews(crews)


class game():
    def __init__(self):
        self.post_msg = ""
        
        with open('data/status.txt', 'r') as stat:
            turn_status = int(stat.readline())
            
        with open('access_token.txt', 'r') as at:
            token = at.readline()
        
        with open('data/cosmicdew.txt', 'r') as dw:
            dew_capt = dw.readline().rstrip('\n')
            dew_ext = dw.readline()
        
        with open('data/gamestatus.txt', 'r') as game:
            game_over = game.readline().rstrip('\n')
            posted = game.readline()
        
        if int(game_over) == 1 and int(posted) == 1:
            sys.exit()
        else:
            self.turn()
            print(self.post_msg)
        
            graph = fb.GraphAPI(access_token = token)
            
            if turn_status == 0:
                all_crews = read_crew()
                comment_teams = ""
                for cid, cmem in all_crews.items():
                    comment_teams += cid.upper() + ':\n' + str(cmem['members']) + '\n\n'
                    
                start_post = graph.put_photo(image = open('pics/start_spaceship.jpg', 'rb'), message = self.post_msg)
                parent_id = start_post['post_id']
                uv_map = graph.put_photo(image = open('universe-stats.png', 'rb'), no_story = True, published = False)
                uv_id = uv_map['id']
                graph.put_object(parent_object = parent_id, connection_name = 'comments', attachment_id = uv_id, message = "Current position of all entities:")
                graph.put_comment(parent_id, comment_teams)
            else:
                post_img = graph.put_photo(image = open('crew-info.png', 'rb'), message = self.post_msg)
                parent_id = post_img['post_id']
                uv_map = graph.put_photo(image = open('universe-current.png', 'rb'), no_story = True, published = False)
                uv_id = uv_map['id']
                graph.put_object(parent_object = parent_id, connection_name = 'comments', attachment_id = uv_id, message = "Current position of all entities:")
            
            turn_status += 1
            with open('data/status.txt', 'w') as stat_write:
                stat_write.write(str(turn_status))
                
            if int(game_over) == 1:
                posted = 1
                with open('data/gamestatus.txt', 'w') as f:
                    f.write(str(game_over) + '\n')
                    f.write(str(posted))
        
    def turn(self):
        with open('data/status.txt', 'r') as f:
            turn = f.readline()

        self.universe_map = Image.new('RGBA', (2000,2000), (255,255,255,255))
        
        if (int(turn) == 0):
            pre_game()
            
            #Setting Planets' Position
            planets = {}
            all_planets = pd.read_csv('data/planets.csv')
            for pindex, p in all_planets.iterrows():
                planet = {}
                planet['type'] = p['Type']
                
                planet_x = random.randint(200, self.universe_map.size[0] - 200)
                planet_y = random.randint(200, self.universe_map.size[1] - 200)
                planet['position'] = (planet_x, planet_y)
                planets[p['Planets']] = planet
            
            config_planets(planets)
            
            #Setting ships' position
            all_crews = read_crew()
            crewCount = 0
            for cid, cvalue in all_crews.items():
                j = 0
                while(j < 5):
                    ship_pos_x = random.randint(100,self.universe_map.size[0] - 100)
                    ship_pos_y = random.randint(100,self.universe_map.size[1] - 100)
                    if(cid == 'crew{}'.format(str(crewCount + 1))):
                        all_crews[cid]['position'] = (ship_pos_x, ship_pos_y)
                        j = 10
                    else:
                        for cid2, cvalue2 in all_crews.items():
                            if (ship_pos_x, ship_pos_y) == all_crews[cid2]['position']:
                                j += 1
                            else:
                                all_crews[cid]['position'] = (ship_pos_x, ship_pos_y)
                                j = 10
                
            config_crews(all_crews)
            self.post_msg = "All ships have left Earth for the search of the Cosmic Dew"
            
            #Drawing...
            draw = ImageDraw.Draw(self.universe_map)
            uv_map_img = Image.open('pics/space/universemap.png')
            self.universe_map.paste(uv_map_img)
            
            planet_font = ImageFont.truetype('pics/fonts/calibril.ttf', 28)
            planet_dot = {"radius": 15, "diff-interior": 5, "ydiff": 20}
            
            for planet_name, planet_stats in planets.items():
                if(planet_stats['type'] != 'Black Hole'):
                    if (planet_stats['type'] == 'X'):
                        continue
                    else:
                        name = planet_name
                        plnt_min_x = planet_stats['position'][0] - planet_dot['radius']
                        plnt_min_y = planet_stats['position'][0] + planet_dot['radius']
                        plnt_max_x = planet_stats['position'][1] - planet_dot['radius']
                        plnt_max_y = planet_stats['position'][1] + planet_dot['radius']
                        
                        name_w, name_h = draw.textsize(name, font = planet_font)
      
                        draw.ellipse((plnt_min_x,plnt_max_x,plnt_min_y,plnt_max_y), fill = random.choice(colors))
                            
                        nametag_coords = (planet_stats['position'][0] - (name_w // 2) - planet_dot['diff-interior'], 
                                          planet_stats['position'][1] + planet_dot['ydiff'],
                                          planet_stats['position'][0] + (name_w // 2) + planet_dot['diff-interior'],
                                          planet_stats['position'][1] + planet_dot['ydiff'] + name_h + (planet_dot['diff-interior'] * 2))
                        draw.rectangle(nametag_coords, fill = "#2e2e2e")
                        draw.text((nametag_coords[0] + planet_dot['diff-interior'], nametag_coords[1] + planet_dot['diff-interior']), name, font = planet_font, align = "center")
                    
            self.universe_map.save('universe-stats.png')
            
        else:
            all_crews = read_crew()
            all_astros = read_astro()
            self.action_code = None
            self.selected_ship_for_action = None
            
            with open('data/cosmicdew.txt', 'r') as f:
                captured_by = f.readline().rstrip('\n')
                extraction = f.readline()
            
            #Decreasing all astros' & ships' stats
            dec_sanity_threshold = random.random()
            for ast_name, ast_stats in all_astros.items():
                if ast_stats['status'] != 'Deceased':
                    if ast_stats['hunger'] > 0:
                        if int(turn) > 50:
                            dec_hunger = random.uniform(2, 5)
                        else:
                            dec_hunger = random.uniform(0, 2)
                        ast_stats['hunger'] -= dec_hunger
                        if ast_stats['hunger'] <= 0:
                            ast_stats['hunger'] = 0
                            dec_thirst = random.uniform(0, 4)
                            ast_stats['thirst'] -= dec_thirst * 2
                            if ast_stats['thirst'] <= 0:
                                ast_stats['thirst'] = 0
                                ast_stats['status'] = 'Deceased'
                                
                                for cid, cstats in all_crews.items():
                                    if ast_name in cstats['members']:
                                        self.selected_ship_for_action = cid
                                        self.post_msg = "{} from {} did not manage to survive due to extreme hunger and thirst".format(ast_name, cid.upper())
                                        self.action_code = 1
                                        deaths, crewmates = self.count_alive_crewmates(ast_name, all_astros, all_crews)
                                        if deaths == (len(crewmates) - 1):
                                            cstats['status'] = 'Destroyed'
                                            self.post_msg = "{}, the last crew member of {} didn't manage to survive due to extreme hunger/thirst \n\nAll crew members of {} did not manage to survive".format(ast_name, cid.upper(), cid.upper())
                                            self.count_remaining(all_crews)
                    
                    if ast_stats['thirst'] > 0:
                        if int(turn) > 50:
                            dec_thirst = random.uniform(2, 5)
                        else:
                            dec_thirst = random.uniform(0, 2)
                        ast_stats['thirst'] -= dec_thirst
                        if ast_stats['thirst'] <= 0:
                            ast_stats['thirst'] = 0
                            ast_stats['status'] = 'Deceased'
                            for cid, cstats in all_crews.items():
                                    if ast_name in cstats['members'] and ast_stats['status'] == 'Alive':
                                        self.selected_ship_for_action = cid
                                        self.post_msg = "{} from {} did not manage to survive due to extreme thirst".format(ast_name, cid.upper())
                                        self.action_code = 1
                                        deaths, crewmates = self.count_alive_crewmates(ast_name, all_astros, all_crews)
                                        if deaths == (len(crewmates) - 1):
                                            cstats['status'] = 'Destroyed'
                                            self.post_msg = "{}, the last crew member of {} didn't manage to survive due to extreme thirst \n\nAll crew members of {} did not manage to survive".format(ast_name, cid.upper(), cid.upper())
                                            self.count_remaining(all_crews)
    
                    if(ast_stats['sanity'] > 0) and (int(turn) % 10 == 0):
                        if int(turn) >= 50:
                            dec_sanity = random.uniform(0, 4)
                        else:
                            dec_sanity = random.uniform(0, 1.5)
                        ast_stats['sanity'] -= dec_sanity
                        
                        if ast_stats['sanity'] <= 0:
                            ast_stats['sanity'] = 0
                            ast_stats['status'] = 'Deceased'
                            for cid, cstats in all_crews.items():
                                    if (ast_name in cstats['members']) and (ast_stats['status'] == 'Alive'):
                                        self.selected_ship_for_action = cid
                                        self.post_msg = "{} from {} lost his/her sanity and jumped into space".format(ast_name, cid.upper())
                                        self.action_code = 1
                                        deaths, crewmates = self.count_alive_crewmates(ast_name, all_astros, all_crews)
                                        if deaths == (len(crewmates) - 1):
                                            cstats['status'] = 'Destroyed'
                                            self.post_msg = "{}, the last crew member of {} lost his/her sanity and jumped into space\n\nAll crew members of {} did not manage to survive".format(ast_name, cid.upper(), cid.upper())
                                            self.count_remaining(all_crews)
                                        
                            else:
                                for cid, cstats in all_crews.items():
                                    if cstats['members'] == crewmates:
                                        self.selected_ship_for_action = cid
                                        self.post_msg = "{}, crew member of {}, lost his/her sanity and jumped into space...".format(ast_name, cid.upper())
                                        self.action_code = 1
            
            for crew_id, crew_ship in all_crews.items():
                if crew_ship['oxygen'] > 0:
                    dec_o2 = random.uniform(0, 0.5)
                    crew_ship['oxygen'] -= dec_o2
                    
                    if crew_ship['oxygen'] <= 0:
                        crew_ship['oxygen'] = 0
                        crew_ship['status'] = 'Destroyed'
                        for m in crew_ship['members']:
                            for ast_name, ast_stats in all_astros.items():
                                if ast_name == m:
                                    ast_stats['status'] = 'Deceased'
                                
                        self.selected_ship_for_action = crew_id
                        self.post_msg = "{}'s spaceship ran out of oxygen, all crew members did not manage to survive".format(self.selected_ship_for_action)
                        self.count_remaining(all_crews)
                        self.action_code = 1                            
            
            #Moving the ships to other locations based on speed
            for crew_id, crew_ship in all_crews.items():
                if crew_ship['status'] == 'Active':
                    curr_posx, curr_posy = crew_ship['position'][0], crew_ship['position'][1]
                    ship_speed = crew_ship['speed']
                    
                    min_x_travel = curr_posx - (ship_speed * 3)
                    max_x_travel = curr_posx + (ship_speed * 3)
                    min_y_travel = curr_posy - (ship_speed * 3)
                    max_y_travel = curr_posy + (ship_speed * 3)
                    if min_x_travel <= 100:
                        min_x_travel = 100
                    if max_x_travel >= self.universe_map.size[0] - 100:
                        max_x_travel = self.universe_map.size[0] - 100
                    if min_y_travel <= 100:
                        min_y_travel = 100
                    if max_y_travel >= self.universe_map.size[1] - 100:
                        max_y_travel = self.universe_map.size[1] - 100
     
                    travel_to = []
                    travel_coord_x = random.randint(min_x_travel, max_x_travel)
                    travel_coord_y = random.randint(min_y_travel, max_y_travel)
                    travel_to.append(travel_coord_x)
                    travel_to.append(travel_coord_y)
    
                    crew_ship['position'] = travel_to
            
            if self.selected_ship_for_action is None:
                #Scanning nearby entities
                all_planets = read_planets()
                scannable = {}
                
                swap = False

                for crewid, crew in all_crews.items():
                    if crew['status'] == 'Active':
                        scan_distance = crew['radar']
                        all_scanned_entities = {}
                        for entity_id, entity in all_crews.items():
                            if(entity_id != crewid) and (math.pow((entity['position'][0] - crew['position'][0]), 2) + math.pow((entity['position'][1] - crew['position'][1]), 2) < math.pow(scan_distance, 2)) and (entity['status'] == 'Active'):
                                all_scanned_entities[entity_id] = "spaceship"
                        for planet_name, planet in all_planets.items():
                            if(math.pow((planet['position'][0] - crew['position'][0]), 2) + math.pow((planet['position'][1] - crew['position'][1]), 2) < math.pow(scan_distance, 2)) and planet['type'] != 'Planet':
                                if planet_name == 'Cosmic Dew' and captured_by != '-':
                                    continue
                                else:
                                    all_scanned_entities[planet_name] = planet['type']
        
                        if len(all_scanned_entities) != 0:
                            scannable[crewid] = all_scanned_entities
                
                if len(scannable) == 0:
                    peaceful = random.random()
                    if peaceful > 0.6:
                        scenarios = ['got struck by an asteroid and got completely destroyed\n\n', 'exploded in deep space and got completely destroyed\n\n', 'got abducted by aliens and disappeared\n\n', 'transcended into the sixth dimension and disappeared\n\n']
                        alive = []
                        for cid, cstats in all_crews.items():
                            if cstats['status'] == 'Active':
                                alive.append(cid)
                        self.selected_ship_for_action = random.choice(alive)
                        
                        for cid, cstats in all_crews.items():
                            if cid == self.selected_ship_for_action:
                                cstats['status'] = 'Destroyed'
                                for m in cstats['members']:
                                    all_astros[m]['status'] = 'Deceased'
                        
                        self.post_msg = "{}'s spaceship {}".format(self.selected_ship_for_action.upper(), random.choice(scenarios))
                        self.count_remaining(all_crews)
                        
                        if captured_by.lower() == self.selected_ship_for_action.lower():
                            captured_by = '-'
                            extraction = 0

                            dew_x = random.randint(200, self.universe_map.size[0] - 200)
                            dew_y = random.randint(200, self.universe_map.size[1] - 200)
                            all_planets['Cosmic Dew']['position'] = (dew_x, dew_y)

                            self.post_msg += "\n\nThe Cosmic Dew is relocated to somewhere in the universe again..."
                        
                        self.action_code = 1
                    else:
                        self.post_msg = "No one attacked no one, it was a peaceful day...\n\nThe previous photo will be posted"
                        self.action_code = 0
                
                else:
                    #Randomly chooses where should the selected crew go
                    self.selected_ship_for_action = random.choice(list(scannable.keys()))
                    target = random.choice(list(scannable[self.selected_ship_for_action].keys()))
                    target_type = scannable[self.selected_ship_for_action][target]
                    
                    if(target_type.lower() == 'spaceship'):
                        self.post_msg = "{} launched an attack on {}'s spaceship".format(self.selected_ship_for_action.upper(), target.upper())
                        selected_weapon_range = all_crews[self.selected_ship_for_action]['weapon']['range']
                        distance = math.sqrt(math.pow(all_crews[target]['position'][0] - all_crews[self.selected_ship_for_action]['position'][0],2) + math.pow(all_crews[target]['position'][1] - all_crews[self.selected_ship_for_action]['position'][1],2))
                        
                        if(distance > selected_weapon_range):
                            all_crews[target]['status'] = 'Destroyed'
                            for crew_member in all_crews[target]['members']:
                                all_astros[crew_member]['status'] = 'Deceased'
                                
                            self.post_msg += ", {}'s spaceship is completely destroyed".format(target.upper())
                            self.count_remaining(all_crews)
                            
                            if captured_by.lower() == target.lower():
                                captured_by = self.selected_ship_for_action
                                swap = True
                                extraction = 0
                                self.post_msg += "\n\n{} has captured the Cosmic Dew! Extraction restarting...".format(self.selected_ship_for_action.upper(), extraction)
                                
                        else:
                            hit_oxygen_tanks = random.random()
                            if(hit_oxygen_tanks > 0.9):
                                damage_caused = random.randint(all_crews[self.selected_ship_for_action]['weapon']['attack'], all_crews[target]['oxygen'] // 2)
                                
                                if(damage_caused > all_crews[target]['oxygen'] // 2):
                                    severe_status = 'heavy'
                                else:
                                    severe_status = 'minor'
                                    
                                all_crews[target]['oxygen'] -= damage_caused
                                self.post_msg += ", the attack did {} damage to the oxygen tanks\n\nThe oxygen level in {}'s spaceship is decreasing".format(severe_status, target.upper())
                                
                            else:
                                self.post_msg += ", but it didn't hit {}'s spaceship".format(target.upper())
                        
                        self.action_code = 2
                        
                    elif(target_type.lower() == 'black hole'):
                        all_crews[self.selected_ship_for_action]['status'] = 'Destroyed'
                        for crew_member in all_crews[self.selected_ship_for_action]['members']:
                            all_astros[crew_member]['status'] = '???'
                        
                        self.post_msg = "{}'s spaceship got sucked into a black hole and disappeared...".format(self.selected_ship_for_action.upper())
                        self.count_remaining(all_crews)
                        self.action_code = 1
                        
                        if captured_by.lower() == self.selected_ship_for_action.lower():
                            captured_by = '-'
                            extraction = 0
                            dew_x = random.randint(200, self.universe_map.size[0] - 200)
                            dew_y = random.randint(200, self.universe_map.size[1] - 200)
                            all_planets['Cosmic Dew']['position'] = (dew_x, dew_y)
                            self.post_msg += "\n\nThe Cosmic Dew is relocated to somewhere in the universe again..."
                    
                    elif(target_type.lower().endswith('star')):
                        all_crews[self.selected_ship_for_action]['status'] = 'Destroyed'
                        for crew_member in all_crews[self.selected_ship_for_action]['members']:
                            all_astros[crew_member]['status'] = 'Deceased'
                        
                        self.post_msg = "{}'s spaceship flew too close to {} and got completely destroyed...".format(self.selected_ship_for_action.upper(), target)
                        self.count_remaining(all_crews)
                        self.action_code = 1
        
                        if captured_by.lower() == self.selected_ship_for_action.lower():
                            captured_by = '-'
                            extraction = 0
                            i = 0
                            dew_x = random.randint(200, self.universe_map.size[0] - 200)
                            dew_y = random.randint(200, self.universe_map.size[1] - 200)
                            all_planets['Cosmic Dew']['position'] = (dew_x, dew_y)
                            self.post_msg += "\n\nThe Cosmic Dew is relocated to somewhere in the universe again..."

                    elif(target_type.lower() == 'x') and (captured_by == '-'):
                        captured_by = self.selected_ship_for_action
                        self.action_code = 1
                        extraction = 0
                        self.post_msg += "{} has captured the Cosmic Dew!".format(self.selected_ship_for_action.upper(), extraction)
                    
                if captured_by != '-':
                    all_planets['Cosmic Dew']['position'] = all_crews[captured_by]['position']

                if not(swap) and captured_by != '-':
                    self.post_msg += "\n\nExtraction process by {}: \n".format(captured_by.upper())
                    
                    cir_total = 20
                    cir_string = ""
                    process = int(extraction) // 5
                    for i in range(process):
                        cir_string += "● "
                    for j in range(cir_total - process):
                        cir_string += "○ "
                    
                    self.post_msg += cir_string
                    self.post_msg += '[{}/100]'.format(extraction)
                    
                    if int(extraction) == 100:
                        with open('data/gamestatus.txt', 'r') as check_posted:
                            game_over = check_posted.readline().rstrip('\n')
                            posted = check_posted.readline()
                        
                        if int(game_over) == 1 and int(posted) == 1:
                            sys.exit()
                        else:
                            if int(game_over) == 0:
                                for crewid, crewship in all_crews.items():
                                    if crewid != captured_by:
                                        crewship['status'] = 'Destroyed'
                                        for a_name, a_stats in all_astros.items():
                                            if a_name not in crewship['members']:
                                                a_stats['status'] = 'Deceased'
                                            
                                self.post_msg += "\n{} completed the extraction process of the Cosmic Dew! All other crews are evaporated into dust and atoms...".format(captured_by.upper())
                                self.selected_ship_for_action = captured_by
                                self.action_code = 1
                                
                                game_over = 1
                                posted = 1
                            
                                with open('data/gamestatus.txt', 'w') as game:
                                    game.write(str(game_over) + '\n')
                                    game.write(str(posted))
                                    
                    else: 
                        extraction = str(int(extraction) + 5)
                        if int(extraction) > 100:
                            extraction = 100
                            game_over = 1
                            posted = 0
                            with open('data/gamestatus.txt', 'w') as game:
                                game.write(str(game_over) + '\n')
                                game.write(str(posted))
                
                config_planets(all_planets)
                
            with open('data/cosmicdew.txt', 'w') as f:
                f.write(str(captured_by) + '\n')
                f.write(str(extraction))
            
            with open('data/action.txt', 'w') as f:
                f.write(str(self.action_code))
            
            #Drawing universe map for the comments first
            draw = ImageDraw.Draw(self.universe_map)
            current_universe = Image.open('universe-stats.png')
            self.universe_map.paste(current_universe)
            
            crew_no_font = ImageFont.truetype('pics/fonts/calibri.ttf', 30)
            ship = {"diff-interior": 5}
            
            for cid, crew_ship in all_crews.items():
                if crew_ship['status'] != 'Destroyed':
                    w, h = draw.textsize(cid.lstrip('crew'), font = crew_no_font)
                    ship_min_x, ship_max_x = (crew_ship['position'][0] - (w // 2) - ship['diff-interior'], crew_ship['position'][0] + (w // 2) + ship['diff-interior'])
                    ship_min_y, ship_max_y = (crew_ship['position'][1] - (h // 2) - ship['diff-interior'], crew_ship['position'][1] + (h // 2) + ship['diff-interior'])
                    draw.rectangle((ship_min_x, ship_min_y, ship_max_x, ship_max_y), fill = '#bdbdbd')
                    draw.text((ship_min_x + ship['diff-interior'], ship_min_y + ship['diff-interior']), cid.lstrip('crew'), font = crew_no_font, fill = 'black', align = 'center')

            dew_font = ImageFont.truetype('pics/fonts/calibril.ttf', 28)
            dew_dot = {"radius": 15, "diff-interior": 5, "ydiff": 20}
            dname = 'Cosmic Dew'
            dname_w, dname_h = draw.textsize(dname, font = dew_font)
            if captured_by != '-':
                d_min_x = all_crews[captured_by]['position'][0] - dew_dot['radius']
                d_min_y = all_crews[captured_by]['position'][0] + dew_dot['radius']
                d_max_x = all_crews[captured_by]['position'][1] - dew_dot['radius']
                d_max_y = all_crews[captured_by]['position'][1] + dew_dot['radius']
                dnametag_coords = (all_crews[captured_by]['position'][0] - (dname_w // 2) - dew_dot['diff-interior'], 
                  all_crews[captured_by]['position'][1] + dew_dot['ydiff'],
                  all_crews[captured_by]['position'][0] + (dname_w // 2) + dew_dot['diff-interior'],
                  all_crews[captured_by]['position'][1] + dew_dot['ydiff'] + dname_h + (dew_dot['diff-interior'] * 2))

            else:
                all_planets = read_planets()
                d_min_x = all_planets['Cosmic Dew']['position'][0] - dew_dot['radius']
                d_min_y = all_planets['Cosmic Dew']['position'][0] + dew_dot['radius']
                d_max_x = all_planets['Cosmic Dew']['position'][1] - dew_dot['radius']
                d_max_y = all_planets['Cosmic Dew']['position'][1] + dew_dot['radius']
                dnametag_coords = (all_planets['Cosmic Dew']['position'][0] - (dname_w // 2) - dew_dot['diff-interior'], 
                  all_planets['Cosmic Dew']['position'][1] + dew_dot['ydiff'],
                  all_planets['Cosmic Dew']['position'][0] + (dname_w // 2) + dew_dot['diff-interior'],
                  all_planets['Cosmic Dew']['position'][1] + dew_dot['ydiff'] + dname_h + (dew_dot['diff-interior'] * 2))


            draw.ellipse((d_min_x,d_max_x,d_min_y,d_max_y), fill = cosmic_dew['color'])
                
            draw.rectangle(dnametag_coords, fill = "#2e2e2e")
            draw.text((dnametag_coords[0] + dew_dot['diff-interior'], dnametag_coords[1] + dew_dot['diff-interior']), dname, font = dew_font, align = "center")

            self.universe_map.save('universe-current.png')
            
            #Drawing the main pic - the crew
            with open('data/action.txt', 'r') as f:
                ind = int(f.readline())
                
            
            crew_info = Image.new('RGBA', (720,720), (255,255,255,255))
            draw_crew = ImageDraw.Draw(crew_info)
            
            directory = os.listdir('pics/reps')
            #First type of image (Not attacking)
            if ind == 1:
                status = ['HUNGER', 'THIRST', 'SANITY', 'STATUS']
                crew_bg = Image.open('pics/crew-bg.png')
                crew_info.paste(crew_bg)
                for member in all_crews[self.selected_ship_for_action]['members']:
                    for file in directory:
                        if file.endswith('.jpg') or file.endswith('.png'):
                            filename, fileext = os.path.splitext(file)
                            if (filename.lower() == member.lower()):
                                mem = Image.open('pics/reps/{}'.format(file))
                                mem = mem.resize((crew_pic[ind]['members_layout']['size'], crew_pic[ind]['members_layout']['size']), Image.ANTIALIAS)
                                crew_info.paste(mem, (crew_pic[ind]['members_layout']['x'], crew_pic[ind]['members_layout']['y'][all_crews[self.selected_ship_for_action]['members'].index(member)]))
                                
                                members_font = ImageFont.truetype('pics/fonts/Neutronium.ttf', 30)
                                crewname_font = ImageFont.truetype('pics/fonts/Neutronium.ttf', 36)
                                status_font = ImageFont.truetype('pics/fonts/Neutronium.ttf', 12)
                                
                                cn_w, cn_h = draw_crew.textsize(self.selected_ship_for_action, font = crewname_font)
                                draw_crew.text((crew_info.size[0] // 2 - cn_w // 2, 30), self.selected_ship_for_action.upper(), font = crewname_font, align = 'center')
                                
                                if all_astros[member]['status'] == 'Deceased' or all_astros[member]['status'] == '???':
                                    tint = Image.open('pics/tint-members.png')
                                    tint = tint.resize((crew_pic[ind]['members_layout']['size'], crew_pic[ind]['members_layout']['size']), Image.ANTIALIAS)
                                    crew_info.paste(tint, (crew_pic[ind]['members_layout']['x'], crew_pic[ind]['members_layout']['y'][all_crews[self.selected_ship_for_action]['members'].index(member)]), mask = tint)
                                
                                draw_crew.text((crew_pic[ind]['members_layout']['name_x'], crew_pic[ind]['members_layout']['y'][all_crews[self.selected_ship_for_action]['members'].index(member)]), filename.upper(), font = members_font, align = 'left')
                                for s in status:
                                    draw_crew.text((crew_pic[ind]['members_layout']['name_x'],
                                                    crew_pic[ind]['members_layout']['y'][all_crews[self.selected_ship_for_action]['members'].index(member)] + 
                                                    crew_pic[ind]['members_layout']['statusbar_ydiff'] +
                                                    crew_pic[ind]['members_layout']['statusbar_h'] * status.index(s) +
                                                    crew_pic[ind]['members_layout']['statusbar_space'] * status.index(s)), s, 
                                                   font = status_font, align = 'left')
                                    
                                    statusbar_y = crew_pic[ind]['members_layout']['y'][all_crews[self.selected_ship_for_action]['members'].index(member)] + crew_pic[ind]['members_layout']['statusbar_ydiff'] + crew_pic[ind]['members_layout']['statusbar_h'] * status.index(s) + crew_pic[ind]['members_layout']['statusbar_space'] * status.index(s)
                                    
                                    if status.index(s) == (len(status) - 1):
                                        draw_crew.text((crew_pic[ind]['members_layout']['statusbar_x'], statusbar_y), all_astros[member][s.lower()].upper(), font = status_font, align = "left")
                                    else:
                                        percentage = round(all_astros[member][s.lower()] / 100 * crew_pic[ind]['members_layout']['statusbar_w'])
                                        
                                        if percentage > 80:
                                            fill = 'green'
                                        elif percentage <= 40:
                                            fill = 'red'
                                        else:
                                            fill = '#d4a839'
                                        
                                        draw_crew.rectangle((crew_pic[ind]['members_layout']['statusbar_x'], statusbar_y,
                                                             crew_pic[ind]['members_layout']['statusbar_x'] + percentage,
                                                             statusbar_y + crew_pic[ind]['members_layout']['statusbar_h']
                                                             ), fill = fill)
                            
                crew_info.save('crew-info.png')
            #Second type of image (Attacking)
            elif ind == 2:
                attack_bg = Image.open('pics/crew-attack.png')
                attack_bg = attack_bg.resize(crew_info.size, Image.ANTIALIAS)
                crew_info.paste(attack_bg)
                                
                wrap_text = textwrap.TextWrapper(width = 10)
                members_font = ImageFont.truetype('pics/fonts/Neutronium.ttf', 18)
                crewname_font = ImageFont.truetype('pics/fonts/Neutronium.ttf', 36)
                others_font = ImageFont.truetype('pics/fonts/calibriz.ttf', 28)
                
                aw, ah = draw_crew.textsize(self.selected_ship_for_action.upper(), font = crewname_font)
                draw_crew.text((crew_info.size[0] // 2 - aw // 2, 30), self.selected_ship_for_action.upper(), font = crewname_font, align = 'center')
                tw, th = draw_crew.textsize(target.upper(), font = crewname_font)
                draw_crew.text((crew_info.size[0] // 2 - tw // 2, crew_info.size[1] - 30 - th), target.upper(), font = crewname_font, align = 'center')
                
                for member in all_crews[self.selected_ship_for_action]['members']:
                    for file in directory:
                        if file.endswith('.jpg') or file.endswith('.png'):
                            filename, fileext = os.path.splitext(file)
                            if (filename.lower() == member.lower()):
                                mem = Image.open('pics/reps/{}'.format(file))
                                mem = mem.resize((crew_pic[ind]['members_layout']['size'], crew_pic[ind]['members_layout']['size']), Image.ANTIALIAS)
                                crew_info.paste(mem, (crew_pic[ind]['members_layout']['x'][all_crews[self.selected_ship_for_action]['members'].index(member)], crew_pic[ind]['members_layout']['y_attacker']))
                                if all_astros[member]['status'] == 'Deceased':
                                    tint = Image.open('pics/tint-members.png')
                                    tint = tint.resize((crew_pic[ind]['members_layout']['size'], crew_pic[ind]['members_layout']['size']), Image.ANTIALIAS)
                                    crew_info.paste(tint, (crew_pic[ind]['members_layout']['x'][all_crews[self.selected_ship_for_action]['members'].index(member)], crew_pic[ind]['members_layout']['y_attacker']), mask = tint)
                                
                                wrapped = wrap_text.wrap(filename.upper())
                                text = ""
                                
                                for line in wrapped:
                                    if ((wrapped.index(line) + 1) == len(wrapped)):
                                        text += line
                                    else:
                                        text += line + '\n'
                                
                                txt_w, txt_h = draw_crew.textsize(text, font = members_font)
                                txt_x = crew_pic[ind]['members_layout']['x'][all_crews[self.selected_ship_for_action]['members'].index(member)] + (crew_pic[ind]['members_layout']['size'] / 2) - (txt_w / 2)
                                draw_crew.text((txt_x, crew_pic[ind]['members_layout']['y_attacker'] + crew_pic[ind]['members_layout']['size'] + 5), text, font = members_font, align = 'center')
                                
                                atk_w, atk_h = draw_crew.textsize('ATTACKED', font = others_font)
                                draw_crew.text((crew_info.size[0] / 2 - atk_w / 2, crew_info.size[1] / 2 - atk_h / 2 - 20), 'ATTACKED', font = others_font, align = 'center')
                                
                for target_cm in all_crews[target]['members']:
                    for tfile in directory:
                        if tfile.endswith('.jpg') or tfile.endswith('.png'):
                            tfilename, tfileext = os.path.splitext(tfile)
                            if (tfilename.lower() == target_cm.lower()):
                                tmem = Image.open('pics/reps/{}'.format(tfile))
                                tmem = tmem.resize((crew_pic[ind]['members_layout']['size'], crew_pic[ind]['members_layout']['size']), Image.ANTIALIAS)
                                crew_info.paste(tmem, (crew_pic[ind]['members_layout']['x'][all_crews[target]['members'].index(target_cm)], crew_pic[ind]['members_layout']['y_target']))
                                if all_astros[target_cm]['status'] == 'Deceased':
                                    tint = Image.open('pics/tint-members.png')
                                    tint = tint.resize((crew_pic[ind]['members_layout']['size'], crew_pic[ind]['members_layout']['size']), Image.ANTIALIAS)
                                    crew_info.paste(tint, (crew_pic[ind]['members_layout']['x'][all_crews[target]['members'].index(target_cm)], crew_pic[ind]['members_layout']['y_target']), mask = tint)

                                wrapped = wrap_text.wrap(tfilename.upper())
                                text = ""
                                
                                for line in wrapped:
                                    if ((wrapped.index(line) + 1) == len(wrapped)):
                                        text += line
                                    else:
                                        text += line + '\n'
                                
                                txt_w, txt_h = draw_crew.textsize(text, font = members_font)
                                txt_x = crew_pic[ind]['members_layout']['x'][all_crews[target]['members'].index(target_cm)] + (crew_pic[ind]['members_layout']['size'] / 2) - (txt_w / 2)
                                draw_crew.text((txt_x, crew_pic[ind]['members_layout']['y_target'] - 5 - txt_h), text, font = members_font, align = 'center')
                                
                                if all_crews[target]['status'] != 'Destroyed':
                                    tw, th = draw_crew.textsize('SURVIVED', font = others_font)
                                    draw_crew.text((crew_info.size[0] / 2 - tw / 2, crew_info.size[1] / 2 + 20), 'SURVIVED', font = others_font, align = 'center', fill = 'green')

                                else:
                                    crew_tint = Image.open('pics/tint-defeated.png')
                                    #crew_tint = crew_tint.resize((crew_info.size[0], crew_info.size[1] // 2), Image.ANTIALIAS)
                                    crew_info.paste(crew_tint, (0, crew_info.size[1] // 2), mask = crew_tint)
                                    tw, th = draw_crew.textsize('DESTROYED', font = others_font)
                                    draw_crew.text((crew_info.size[0] / 2 - tw / 2, crew_info.size[1] / 2 + 20), 'DESTROYED', font = others_font, align = 'center', fill = 'red')
                                
                crew_info.save('crew-info.png')
            
            config_astro(all_astros)
            config_crews(all_crews)
            
        
    def count_remaining(self, allcrews):
        counter = 0
        for cid, cstatus in allcrews.items():
            if cstatus['status'] == 'Active':
                counter += 1
        self.post_msg += "\n\n{} crews remaining".format(str(counter))
        if counter == 1:
            with open('data/gamestatus.txt', 'r') as game:
                game_over = game.readline().rstrip('\n')
                posted = game.readline()
                
                if int(game_over) == 1 and int(posted) == 1:
                    sys.exit()
                else:
                    if int(game_over) == 0:
                        self.post_msg += "\n\nThere is only one crew left. "
                    
                        with open('data/cosmicdew.txt', 'r') as f:
                            captured = f.readline().rstrip('\n')
                            ext = f.readline()
                        
                        if captured == '-':
                            self.post_msg += "All crews failed to obtain the Cosmic Dew. Game over."
                        else:
                            self.post_msg += "The Cosmic Dew is obtained, but not 100% extracted. The only crew decides to return to Earth to continue the extraction process. Game over."
                        
                        game_over = 1
                        posted = 1
                        with open('data/gamestatus.txt', 'w') as game:
                            game.write(str(game_over) + '\n')
                            game.write(str(posted))

        return counter
                
    def count_alive_crewmates(self, own, allastros, allcrews):
        death_counter = 0
        crewmates = []
        for c_id, c_stats in allcrews.items():
            if own in c_stats['members']:
                crewmates = c_stats['members']
                for member in c_stats['members']:
                    if member != own:
                        for a_name, a_stats in allastros.items():
                            if a_name == member and a_stats['status'] == 'Deceased':
                                death_counter += 1
        return death_counter, crewmates

            
game()


"""
To do list (After hackathon when I am free):
    Supergiant star explosion and engulfing
    Sabotages
    Planet scenarios
    Ship scenarios (sabotage, someone died in the ship for not opening the radiation filter...)
    Better speed, instead of teleporting here and there
    Food and Water replenish (For now it will only decrease, no increase)
    Kills leaderboard
"""