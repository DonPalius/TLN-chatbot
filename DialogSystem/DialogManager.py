
from spacy import load
from DepMatcher import DepMatcher
from Utils import load_rules
import pandas as pd
from Nlg import *
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
from TextToSpeech import *
from SpeechToText import *
import math
from pytimedinput import timedInput


class DialogManager:

    def __init__(self):
        self.Nlg = Nlg()
        self.TextToSpeech = TextToSpeech()
        self.SpeechToText = SpeechToText()
        # Initialize Dependency matcher with rules
        self.dep_matcher = DepMatcher()
        # Initialize dict of actual potions and ingredients
        self.actual_frame = {}
        self.wrong_word = [
            "first",
            "second",
            "third",
            "fourth",
            "fith",
            "sixth",
            "ingredient",
            "I"]
        self.check_ingredient_presence = False
        self.total_try_potion = 0
        self.ingredient_quantity = {}
        self.check_negation = False
        self.max_score = 30
        self.response = None
        self.penalty = 0
        self.total_score = 0
        self.actual_score = 0
        self.position_ingredient = None
        self.idx_potion = 0
        self.question = 0
        self.backup_question = 0
        self.check_partial_ingredient = False
        self.skip_question = False
        self.question_missing_ingredient = False
        self.question_tricky_question = False
        self.future_penalty = 0
        self.backup_answer = None
        self.timeout = False
        ##if user responde "first" check the first elem in array of ingridient in q3
        self.array_q3 = []

        # Initialize User responses frame
        self.response_frame = {}

        # TODO Add list of Ingredients
        # TODO Add List of True Ingredients ?
        # TODO Initialize Empty Frame for responses

        # self.ingredients = []

        # load potions and ingredients dataframe
        df_potions = pd.read_json("Data/test_potion.json")
        # select random potion
        df_potions = df_potions.sample(n=3)
        # preprocessing phase -> cleanup dataframe and create response frame
        # and actual frame with the selected potion
        for item in df_potions[0].index.to_list():
            tmp_dict = df_potions.loc[item].to_dict()
            for i in range(0, len(
                    list(df_potions.loc[df_potions.index[0]].to_dict().values()))):
                if tmp_dict[i] == "" or math.isnan(float()):
                    del tmp_dict[i]
                if isinstance(tmp_dict[i], float) and math.isnan(tmp_dict[i]):
                    del tmp_dict[i]
            self.actual_frame[item] = tmp_dict

        myL = list(self.actual_frame.keys())
        frame_q1 = {}
        #case q2 and q3
        empty_frame = {0: None}
        self.response_frame[myL[1]] = empty_frame
        self.response_frame[myL[2]] = empty_frame
        for ingredient in self.actual_frame[myL[0]]:
            frame_q1[ingredient] = None
        self.response_frame[myL[0]] = frame_q1
        # Construct responses dict

        # Initialize current Potion
        self.current_potion = list(self.actual_frame.keys())[self.idx_potion]
        if self.idx_potion == 0:   
            self.total_try_potion = len(self.actual_frame[self.current_potion])
        else:
            self.total_try_potion = 2

        self.check_penalty = False
        # TODO : normalize score
        for i in self.response_frame.keys():
            self.total_score = self.total_score + len(self.response_frame[i])

        # print(self.total_score, " total score")
        self.actual_score = self.total_score

    # check if the potion is complete
    def check_potion_complete(self, response_frame):
        if None in list(response_frame.values()):
            return False
        else:
            return True

    # Check if response ingredient in actual_frame == response_frame

    def check_ingredient_name(self, ingredient):

        for item in range(0, len(self.actual_frame[self.current_potion])):
            # print(f"item {item}")
            # print(
            #     f"true ingredient : {str(self.actual_frame[self.current_potion][item]).lower()}")
            # print(f"ingredient : {ingredient.lower()}")

            if str(self.actual_frame[self.current_potion]
                   [item]).lower() == str(ingredient.lower()):
                return item
        return None

    def get_final_score(self):
        if ((self.actual_score - self.penalty) *
                self.max_score) / self.total_score < 0:
            return 0
        else:
            return ((self.actual_score - self.penalty)
                    * self.max_score) / self.total_score

    def next_question(self):
        # print("-----------", self.idx_potion == len(self.actual_frame) - 1)
        # end of question
        if self.idx_potion == len(self.actual_frame) - 1:
            # print(f"response frame : {self.response_frame}")
            # print(f"actual frame : {self.actual_frame}")
            # if not self.check_potion_complete(self.response_frame[self.current_potion]):
            #     print("Error")
            #     self.increase_penalty(0)
            # else:
                print(f"penalty : {self.penalty}")
                # print(f"actual score : {self.actual_score}")
                # print(f"max score : {self.max_score}")
                # print(f"self.total_score : {self.total_score}")
                final_score = self.get_final_score()
                if final_score >=18:
                    print(
                        f"voto in base  {self.max_score} = {final_score}")
                print(
                    self.Nlg.grade_comment(
                        ((self.actual_score -
                        self.penalty) *
                        self.max_score) /
                        self.total_score))
                return False
        else:
            # print("goto next question")
            # print(f"  self.backup_question : {  self.backup_question}")
            self.backup_question = 0
            # print(f" INDEX POTION : { self.idx_potion}")
            self.idx_potion += 1
            self.current_potion = list(self.actual_frame.keys())[
                self.idx_potion]
            self.question_tricky_question = False
            # update total_try_potion new potion
            self.total_try_potion = 2
            return True

    def increase_penalty(self, future_penalty):
        # case domanda 2 e 3 frame have only one element
        if len(self.response_frame[self.current_potion]) <= 1:
            # if not the first time the user receive a penalty, then I * 2 
            # otherwise I just initialize it
            if self.check_penalty:
                # print("penalty * 2 case low ingredient")
                self.penalty = self.penalty * 2
            else:
                # print("penalty fist case low ingredient")

                self.penalty = self.penalty + 0.5
                self.check_penalty = True
        else:
            # print("skip question")
            # print(
            #     f" idx potion :{self.idx_potion } and self.question_tricky_question : {self.question_tricky_question} ")
            # print(any(
            #         list(self.response_frame[self.current_potion].values())))
            
            # case 1 -> first question and I already responded one time (tricky_question)
            # case 2 -> skip the question
            # case 3 -> timeout
            if self.idx_potion == 0 and self.question_tricky_question or self.skip_question or self.timeout:
                None_elem_rFrame = len(list(filter(lambda a: None is a, list(
                    self.response_frame[self.current_potion].values()))))
                # print(f"self.penalty before check : {self.penalty}")
                # print(f"tmp : {None_elem_rFrame}")

                # count the penalty in base of None element in the frame
                if float(self.penalty) == 0:
                    self.penalty = 0.4
                    # print(f"-------FLOAT : {float(self.penalty) == 0} ")
                    if None_elem_rFrame > 1:
                        if self.question_tricky_question or self.timeout or self.skip_question:
                            self.penalty = self.penalty * None_elem_rFrame
                    else:
                        self.penalty = self.penalty * 0.4
                        # print(f"None_elem_rFrame : {None_elem_rFrame}, self penalty final : {self.penalty}")

                else:
                    if None_elem_rFrame > 1:
                        self.penalty = self.penalty * None_elem_rFrame
                    else:
                        self.penalty = self.penalty * 0.4

                # print(f"None_elem_rFrame : {None_elem_rFrame}, self penalty final : {self.penalty}")
                self.skip_question = False
            else:
                # case simple penalty
                # print(f"future penalty final : {future_penalty}")
                # print(
                # f"response frame :
                # {self.response_frame[self.current_potion]}")
                if future_penalty == 1:
                    self.penalty = self.penalty + 0.10 * 3
                else:
                    # print(f"start penalty : { self.penalty}")
                    self.penalty = self.penalty + 0.10
                    self.penalty = self.penalty * 2 * future_penalty
                    # print(f"new penalty : { self.penalty}")
                self.future_penalty = 0

    def backup_strategy(self):
        # print(f"self.backup_question : {self.backup_question}")
        # print(f" potion : {self.current_potion}")
        if self.backup_question == 1 :
            self.future_penalty = 0
            self.backup_question += 1
            #self.total_try_potion += 1
            print(self.Nlg.backup_question(self.backup_answer))
            return True
        else:
            return False

    def check_backup_strategy(self, response, currentPotion):
        # print(f"check backup strategy : {self.backup_question}")
        # print(f"localcurrentPotion : {currentPotion}, self.current_potion : {self.current_potion}")
        if str(self.current_potion) == str(currentPotion) and self.backup_question == 0 and not any(
                list(self.response_frame[self.current_potion].values())):
            # if all([None == elem for elem in
            # list(self.response_frame[self.current_potion].values())]):
            print(
                self.Nlg.get_comment("neutral"))
            # self.total_try_potion += 1
            # print(f"----{matches}")
            self.backup_answer = response
            self.backup_question = 1
            # print(f"check backup strategy 1: {self.backup_question}")

            return True

        else:
            if self.backup_question > 0:
                # print(f"future penalty : {self.future_penalty}")
                self.increase_penalty(
                    self.future_penalty)
                print(self.Nlg.get_comment("bad_answer"))
            return False

    def input_timer(self, question):
        response = timedInput(f"{question}\n", timeout=60)
        if response[1]:
            self.timeout = True
            self.increase_penalty(0)
            print("You took too long to answer!")
            if not self.next_question():
                return False
        else:
            self.timeout = False
            return response[0]

    def generate_array_ingredient(self, ingredients, rand_ingredient):
        ingredients = list(ingredients.values())
        ingredients.append(rand_ingredient)
        random.shuffle(ingredients)
        self.array_q3 = ingredients
        ingr = ', '.join(ingredients)
        return ingr

    def check_position(self, item_to_check, rand_ingredient):
        for res in item_to_check:
            for idx in self.wrong_word[:5]:
                # print(f" idx  : {idx}, res: {res}" )
                if str(idx).lower() in str(res):
                    # print(f" idx  : {idx}")
                    # print(f"real pos : {self.wrong_word.index(idx)+1}")
                    # print(f" {self.array_q3[self.wrong_word.index(idx)]}")
                    # print(f"rand_ingredient : {rand_ingredient}")
                    if self.array_q3[self.wrong_word.index(
                            idx)] == rand_ingredient:
                        # print("--TRUE-----")
                        return True

        return False

    def start(self):
        # self.TextToSpeech.getResponse(self.Nlg.greetings())
        print(self.Nlg.greetings())
        exit = True
        # print(f"my potion : {self.actual_frame}")
        while exit:
            # for potion in self.actual_frame.keys():
            # self.current_potion = potion

            # TODO Initialize Frame for resposes
            # TODO Initialize Stack for memory of responses
            # TODO Initialize Status of dialog manager
            # TODO Create Phrase for prompt
            check_score = self.get_final_score()
            # print(f"self.total_try_potion {self.total_try_potion}")
            if check_score == 0:
                # print("-----final score------")
                return print(self.Nlg.grade_comment(check_score))
            if self.total_try_potion <= 0:
                # print("self.next_question 0 total try")
                if not self.next_question():
                    break

            else:
                # DOMANDA 1
                response = None
                if self.idx_potion == 0:
                    self.question = 0
                    if self.backup_strategy():
                        response = self.input_timer(
                            self.Nlg.ask_ingredients(self.current_potion))
                    else:
                        if self.question_missing_ingredient:
                            self.question_missing_ingredient = False
                            response = self.input_timer(
                                self.Nlg.missing_ingredients())
                        else:
                            if self.question_tricky_question:
                                response = self.input_timer(
                                    self.Nlg.tricky_question())

                            else:
                                response = self.input_timer(
                                    self.Nlg.ask_ingredients(self.current_potion))
                                # response = timedInput(f"{}\n",timeout = 10)
                                # if response[1]:
                                #     print("timer")
                                #     self.next_question()
                                # else:
                                #     response = response[0]

                # DOMANDA 2
                if self.idx_potion == 1:
                    # print(f"frame : {self.actual_frame}")
                    # print(f" random potion : {self.current_potion}")
                    # print(f"potion ingredient : {self.actual_frame[self.current_potion]}")
                    self.position_ingredient = random.randint(
                        0, len(self.actual_frame[self.current_potion]) - 1)
                    # print(f" random position : {self.position_ingredient}")
                    # print(
                    # f"potion_yes_no :
                    # {self.actual_frame[str(self.current_potion)][self.position_ingredient]}")
                    self.question = 1
                    if self.backup_strategy():
                        response = self.input_timer(self.Nlg.true_false_question(self.actual_frame[str(
                            self.current_potion)][self.position_ingredient], self.current_potion))
                    else:
                        response = self.input_timer(self.Nlg.true_false_question(self.actual_frame[str(
                            self.current_potion)][self.position_ingredient], self.current_potion))

                # DOMANDA 3
                if self.idx_potion == len(self.actual_frame) - 1:
                    actual_frame_values = list(
                        self.actual_frame[self.current_potion].values())
                    rand_ingredient = self.actual_frame[list(self.actual_frame.keys())[self.idx_potion - 1]][random.randint(
                        0, len(self.actual_frame[list(self.actual_frame.keys())[self.idx_potion - 1]].values()) - 1)]
                    while (rand_ingredient in actual_frame_values):
                        rand_ingredient = self.actual_frame[list(self.actual_frame.keys())[self.idx_potion - 1]][random.randint(
                            0, len(self.actual_frame[list(self.actual_frame.keys())[self.idx_potion - 1]].values()) - 1)]
                    if rand_ingredient not in list(
                            self.actual_frame[self.current_potion].values()):
                        self.question = 2
                        if self.backup_strategy():
                            response = self.input_timer(self.Nlg.find_wrong_question(
                                self.current_potion, self.generate_array_ingredient(self.actual_frame[self.current_potion], rand_ingredient)))
                        else:
                            response = self.input_timer(self.Nlg.find_wrong_question(
                                self.current_potion, self.generate_array_ingredient(self.actual_frame[self.current_potion], rand_ingredient)))
                    
                        if not response:
                            return

                if response.lower() == "exit":
                    break
                else:
                    if "next question" in response.lower():
                        self.skip_question = True
                        self.increase_penalty(0)
                        # print("skip question")
                        if not self.next_question():
                            return
                    else:
                        if len(response) == 0:
                            # print(f"try : {self.total_try_potion}")
                            print(self.Nlg.get_comment("neutral"))
                        else:
                            self.current_potion = list(self.actual_frame.keys())[
                                self.idx_potion]
                            # print(f"response.lower() : {response.lower()}")
                            match = self.dep_matcher.get_matches(response)
                            matches = []
                            print(f"match : {match}")
                            local_currentPotion = self.current_potion
                            # cleaning match list from useless output
                            if self.idx_potion != 2 or self.question != 2:
                                for value in match:
                                    valueToRemove = [
                                        elem in value[1].lower() for elem in self.wrong_word]
                                    if not any(valueToRemove):
                                        matches.append(value)
                            else:
                                matches = match
                                

                            if len(matches) == 0 :
                                if self.idx_potion == 2:
                                    if self.check_position(
                                        word_tokenize(response.lower()), rand_ingredient):
                                        print(
                                            self.Nlg.get_comment("good_answer"))
                                        if not self.next_question():
                                            return

                                else:
                                    print(self.Nlg.get_comment("neutral"))
                            else:
                                # check if i finished the total try for this potion
                                    # print(f"matches : {matches}")
                                    local_currentPotion = self.current_potion
                                    self.total_try_potion -= 1
                                    # print(f"self.total_try_potion : {self.total_try_potion}")
                                    for item in matches:
                                        # print(
                                        # f"total try : {self.total_try_potion}")
                                        if item[0] == "yesOrNo":
                                            # DOMANDA 1 pt2
                                            if self.question_tricky_question:
                                                # are you sure all ingredient has beeen listed ?
                                                # check if true or false
                                                # print(item[1] == "yes")
                                                if str(item[1]).lower() == "yes":
                                                    if self.check_potion_complete(
                                                            self.response_frame[self.current_potion]):
                                                        # print(
                                                        #     "CASE YES E FRAME COMPLETO")
                                                        print(
                                                            self.Nlg.get_comment("good_answer"))
                                                        # correct answer check if
                                                        # it's complete
                                                        if not self.next_question():
                                                            break
                                                            # print(
                                                            #     "next question 1")
                                                    else:
                                                        # print(
                                                        #     "CASE YES E FRAME NON COMPLETO")
                                                        self.increase_penalty(0)
                                                        print(self.Nlg.get_comment(
                                                            "bad_answer"))
                                                        if not self.next_question():
                                                            break

                                                if str(item[1]).lower() == "no" and not self.check_potion_complete(
                                                        self.response_frame[self.current_potion]):
                                                    self.question_missing_ingredient = True
                                                if str(item[1]).lower() == "no" and self.check_potion_complete(
                                                        self.response_frame[self.current_potion]):
                                                    # print("COMMENTO NEGATIVO")
                                                    print(self.Nlg.get_comment(
                                                        "bad_answer"))
                                                    self.increase_penalty(0)
                                                    if not self.next_question():
                                                        # print("next question 1")
                                                        break
                                            # DOMANDA 2
                                            # in this question piton ask if the
                                            # ingredient X is present in the potion
                                            # Y
                                            elif self.question == 1:
                                                # yes, ___ is present
                                                # no, ___ isn't present
                                                # print(
                                                #     self.actual_frame[self.current_potion][self.position_ingredient])
                                                idx_yes_no_potion = self.check_ingredient_name(
                                                    self.actual_frame[self.current_potion][self.position_ingredient])
                                                if str(item[1]).lower() == "yes":
                                                    if idx_yes_no_potion is not None:
                                                        # print(
                                                        # f"current potion :
                                                        # {self.response_frame[self.current_potion]}")
                                                        self.response_frame[self.current_potion] = "yes"
                                                        print(
                                                            self.Nlg.get_comment("good_answer"))
                                                        # print("domanda due risposta esatta")
                                                        if not self.next_question():
                                                            return

                                                    else:
                                                        # bad_answer
                                                        print(self.Nlg.get_comment(
                                                            "bad_answer"))
                                                        self.increase_penalty(0)

                                                elif str(item[1]).lower() == "no":
                                                    if idx_yes_no_potion is not None:
                                                        print(self.Nlg.get_comment(
                                                            "bad_answer"))

                                                        # match in ingrediente ->
                                                        # wrong answer
                                                        self.increase_penalty(0)
                                                    else:
                                                        # match in ingrediente ->
                                                        # right answer
                                                        print(self.Nlg.get_comment(
                                                            "good_answer"))
                                                        self.response_frame[self.current_potion] = "no"
                                                        # print("domanda due risposta esatta pt2")
                                                        if not self.next_question():
                                                            return



                                        # DOMANDA 3
                                        # is this question you need to indicate the
                                        # wrong ingredient
                                        if self.question == 2:
                                            # print(f"{str(rand_ingredient).lower()}, {item[1].lower()}")
                                            # print(f"backup_question : {self.backup_question}")
                                            if str(rand_ingredient).lower() == str(
                                                    item[1]).lower():
                                                print(self.Nlg.get_comment(
                                                    "good_answer"))

                                                self.response_frame[self.current_potion] = "right"
                                                # print(
                                                #     self.response_frame[self.current_potion])
                                                if not self.next_question():
                                                    return
                                            # else:
                                            #     if not self.check_backup_strategy(
                                            #             matches, currentPotion):
                                            #         print(
                                            #             self.Nlg.get_comment("bad_answer"))
                                            else:
                                                # print("before check position ELSE")
                                                if self.check_position(
                                                    word_tokenize(response.lower()), rand_ingredient):
                                                    print(
                                                        self.Nlg.get_comment("good_answer"))
                                                    if not self.next_question():
                                                        return

                                        if item[0] == "Is_ingredient" and self.question == 0:
                                            # print(f"future_penalty : {self.future_penalty}")
                                            idx = self.check_ingredient_name(
                                                item[1])
                                            # se idx != None -> match
                                            if idx is not None:
                                                # check if neg right ingredient
                                                if not self.check_negation:
                                                    # print(
                                                    # f" check negation : {
                                                    # self.check_negation}")
                                                    if self.response_frame[self.current_potion][idx] is None:
                                                        # add ingredient in frame
                                                        # -> good_answer
                                                        self.response_frame[self.current_potion][idx] = item[1]

                                                    else:
                                                        # ingredient already in the
                                                        # frame -> neutral comment
                                                        # print(
                                                        #     "ingredient already in the frame")
                                                        print(self.Nlg.get_comment(
                                                            "neutral"))
                                                else:
                                                    # neg right ingredientid 
                                                    # print(self.Nlg.get_comment(
                                                    #     "bad_answer"))
                                                    self.future_penalty += 1
                                                    # print(
                                                    # f"increase future penalty:
                                                    # {self.future_penalty}")
                                                    self.check_negation = not self.check_negation
                                            else:
                                                # print(f" self.check_partial(item[1]) : {self.check_partial(item[1])}")
                                                # if self.check_partial(item[1]):
                                                #     pass
                                                # #   commento stile devi essere piu preciso
                                                # else:

                                                # TODO taggare i match che sono ingredienti cosi da evitare double lavoro
                                                # check if match is part of other
                                                # match and check if the other
                                                # match is an ingredient
                                                myMatches = [elem[1]
                                                            for elem in matches]
                                                if any([item[1] in myMatches[elem] for elem in range(
                                                        0, myMatches.index(item[1]))]):
                                                    listMatches = list(filter(lambda a: item[1] in a, myMatches))
                                                    if len(listMatches) > 0:
                                                        pass

                                                else:
                                                    self.future_penalty += 1
                                                    # print(
                                                    # f"increase future penalty 1:
                                                    # {self.future_penalty}")
                                                    
                                                    # print(self.Nlg.get_comment(
                                                    #     "bad_answer"))

                                        if item[0] == "Is_not_ingredient":
                                            # we'll check if the negated match is
                                            # an ingredient
                                            self.check_negation = True

                                    # print(
                                    #     f"response frame : {self.response_frame[self.current_potion]}")

                                    if self.idx_potion == 0:
                                        # print("HERE")
                                        if self.check_potion_complete(
                                                self.response_frame[self.current_potion]):
                                            print(
                                                self.Nlg.get_comment("good_answer"))
                                            if self.question_tricky_question:
                                                if not self.next_question():
                                                    # print("next question 4")
                                                    break
                                                # print("next question domanda due")
                                                # # scorro prossima pozione
                                                # print("scorro prossima pozione")
                                            else:
                                                self.question_tricky_question = True

                                        else:
                                            self.question_tricky_question = True

                                    # check if the response is completly wrong and
                                    # it is the first time
                                    self.check_backup_strategy(
                                        response.lower(), local_currentPotion)
                                    if self.idx_potion == 0 and self.backup_question > 1:
                                        # print("-----------SET TRICKY QUESTION------")
                                        self.question_tricky_question = True

            # print(f"penalty : {self.penalty}")
            # print(f"actual score : {self.actual_score}")
            # print(f"max score : {self.max_score}")
            # print(f"self.total_score : {self.total_score}")
            # print(
            # f"voto in base  {self.max_score} =
            # {((self.actual_score-self.penalty)*self.max_score)/self.total_score
            # }")

            # if self.idx_potion == len(self.actual_frame)-1 and self.total_try_potion == 0:
            # return
            # print(((self.actual_score - self.penalty)
            #       * self.max_score) / self.total_score)

        return print("exit")


if __name__ == "__main__":
    d = DialogManager()
    d.start()
