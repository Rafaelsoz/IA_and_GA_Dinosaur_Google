from GameClasses.ia_game import GameIA
from IAClasses.genetic_algorithm import GeneticAlgorithm
from constants import draw_esc
import numpy as np
import pygame
import sys


def start_ia_game(screen, num_generations, population_size, target: int = 50000, number_of_elitists: int = 3,
                  inferior_limit_pos: int = 220, upper_limit_pos: int = 221):

    genetic = GeneticAlgorithm(num_generations, population_size, target, number_of_elitists=number_of_elitists,
                               inferior_limit_pos=inferior_limit_pos, upper_limit_pos=upper_limit_pos,
                               start_rate_crossing=0.8, start_rate_mutation=0.2)
    game = GameIA(screen)

    genetic.start_population()
    game.dinosaurs = genetic.population
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    game.end = True
                    game.draw_finished_test()
                    genetic.result_and_save()

                if event.key == pygame.K_ESCAPE:
                    run = False

        if not game.reset and not game.end:
            game.draw_game()
            game.draw_cross_rate(genetic.current_rate_crossing)
            game.draw_mutation_rate(genetic.current_rate_mutation)
            game.draw_expected_score(genetic.expected_score)
            game.draw_stagnant_generations(genetic.stagnant_generations)
            draw_esc(game.screen)
            game.draw_graphics_score()

            game.create_obstacles()
            game.update_obstacles()

            for dinosaur in game.dinosaurs:
                if not dinosaur.dead:
                    info = game.info_game(dinosaur)
                    decision = dinosaur.decision(np.array(info))
                    dinosaur.ia_move(decision)

            game.there_was_collision()

            if game.end_game():
                game.reset = True

            game.update_clouds()
            game.update_score_and_speed()

        if game.current_generation == genetic.num_generations or game.score >= genetic.target:
            if not game.end:
                game.end = True
                game.draw_finished_test()
                genetic.result_and_save()
                draw_esc(game.screen)

        elif game.reset and not game.end:
            game.game_reset()

            genetic.evaluation()
            genetic.elitism()

            # Renewing population if necessary
            if genetic.check_stagnation(game.max_score):
                game.resets_generation += 1
                print(f"Renewing population {game.resets_generation}")

                genetic.start_population()
                game.dinosaurs = genetic.population

                game.hi_score = 0
                game.best_scores = [0]
                game.mean_scores = [0]
                game.current_generation = 0

            # Create new population
            else:
                game.best_scores.append(game.max_score)
                game.mean_scores.append(genetic.get_mean_score())
                print(f"\nCurrent Generation :: {game.current_generation}")
                print(f"Stagnation Generation :: {genetic.stagnant_generations}")
                print(f"Mutation Rate :: {genetic.current_rate_mutation},\t\t "
                      f"Crossing Rate :: {genetic.current_rate_crossing}")
                print(f"Hi-Score :: {game.hi_score}, Max-Score :: {game.max_score}")
                genetic.info_betters()

                genetic.create_new_population()
                genetic.update_rates()
                game.dinosaurs = genetic.population

            game.current_generation += 1

        pygame.display.update()
