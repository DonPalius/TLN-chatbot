from simplenlg.framework import *
from simplenlg.lexicon import *
from simplenlg.realiser.english import *
from simplenlg.phrasespec import *
from simplenlg.features import *
import pandas as pd
import random
from sys import platform


class Nlg:

    good_answer = [
        "You are right Potter",
        "Good Job Potter! ",
        "Well done Potter",
        "That's right Potter! ",
        "That's correct Potter! "]
    bad_answer = [
        "You are wrong as usual! ",
        "Nice try but of course you are wrong. ",
        "That's not correct Potter! "]
    indifferent_answer = ["Answer me in a meaningful way Potter! "]
    neutral_answer = ["I see you confused Potter! "]
    possible_sentences = [
        "Good morning Mr Potter.",
        "Welcome to the potions examination Mr Potter.",
        "Good morning Mr Potter, I hope that you have studied this time.",
        "Good morning Potter, I hope you are better prepared than last time. "]

    def get_comment(self, mood):
        # commenti in base alla penalità
        if mood == "good_answer":
            return random.choice(self.good_answer)

        if mood == "bad_answer":
            return random.choice(self.bad_answer)
        # if mood =="nea_answer":
        #      return self.good_answer[random.choice(self.good_answer)]
        if mood == "neutral":
            return random.choice(self.neutral_answer)

        # return self.good_answer, self.bad_answer

    def greetings(self):
        # frase di benvenuto -> inizio esame
        choose_sentence = list(random.sample(
            range(0, len(self.possible_sentences)), 1))
        return self.possible_sentences[choose_sentence[0]]

    @classmethod
    def grade_comment(self, grade):

        lexicon = Lexicon.getDefaultLexicon()
        realiser = Realiser(lexicon)
        nlgFactory = NLGFactory(lexicon)
        if grade <= 17:
            p = nlgFactory.createClause("See you next time mr. Potter")
        elif grade <= 25:
            p = nlgFactory.createClause("Good Job mr. Potter")
        else:
            p = nlgFactory.createClause("Excellent mr. Potter")

        phrase = realiser.realiseSentence(p)
        return phrase

    @classmethod
    def true_false_question(self, ingredient, potion):
        # risposta incompleta

        lexicon = Lexicon.getDefaultLexicon()
        realiser = Realiser(lexicon)
        nlgFactory = NLGFactory(lexicon)
        p = nlgFactory.createClause(ingredient)
        verb = nlgFactory.createVerbPhrase("is present in " + potion)
        # verb.setPlural(False)
        p.setVerbPhrase(verb)
        p.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.YES_NO)

        phrase = realiser.realiseSentence(p)
        return phrase

        # frame non completo
        # Are you sure that all the ingredients have been listed?

    @classmethod
    def missing_ingredients(self):
        lexicon = Lexicon.getDefaultLexicon()
        nlgFactory = NLGFactory(lexicon)
        realiser = Realiser(lexicon)
        p = nlgFactory.createClause("the remaining ingredients")
        verb = nlgFactory.createVerbPhrase("be")
        verb.isNegated()
        verb.setPlural(True)
        p.setVerbPhrase(verb)
        p.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.YES_NO)
        phrase = realiser.realiseSentence(p)
        return phrase

    @classmethod
    def tricky_question(self):
        lexicon = Lexicon.getDefaultLexicon()
        nlgFactory = NLGFactory(lexicon)
        realiser = Realiser(lexicon)
        case = random.randint(0, 1)
        if case == 0:
            p = nlgFactory.createClause("you", "be sure")
            p0 = nlgFactory.createClause(
                "you have listed all the ingredients")
            p.setComplement(p0)
            p.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.YES_NO)
        elif case == 1:
            # Are you sure you have mentioned all the ingredients?
            p = nlgFactory.createClause("you", "be sure")
            p0 = nlgFactory.createClause(
                "you", "have mentioned", "all the ingredients")
            p.setComplement(p0)
            p.setFeature(Feature.INTERROGATIVE_TYPE,
                         InterrogativeType.YES_NO)

        phrase = realiser.realiseSentence(p)
        return phrase

    @classmethod
    def backup_question(self, backup_answer):
        lexicon = Lexicon.getDefaultLexicon()
        nlgFactory = NLGFactory(lexicon)
        realiser = Realiser(lexicon)
        p = nlgFactory.createClause("you")
        p.setVerb("mean by " + backup_answer)
        p.setSubject("you")
        p.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.WHAT_OBJECT)
        phrase = realiser.realiseSentence(p)
        p0 = nlgFactory.createClause(
            " I will give you another chance")

        phrase1 = realiser.realiseSentence(p0)

        return phrase + " " + phrase1

    @classmethod
    def find_wrong_question(self, potion,random_array):
        """ Generate a tricky question with specified ingredient or not.

        Args:
            to_ask (str): ingredient to ask

        Returns:
            str: generated question
        """
        # print(f"potion {potion}")
        # print(f"ingredients {ingredients}")
        # print(f"rand_ingredient {rand_ingredient}")
        # ingr = []
        # ingredients = list(ingredients.values())
        # ingredients.append(rand_ingredient)
        # random.shuffle(ingredients)
        # ingr = ', '.join(ingredients)

        lexicon = Lexicon.getDefaultLexicon()
        realiser = Realiser(lexicon)
        nlgFactory = NLGFactory(lexicon)
        # Are you sure that all the ingredients have been listed?
        p = nlgFactory.createClause(
            f"{random_array}. Can you tell me the wrong ingredients of {potion}")

        phrase = realiser.realiseSentence(p)

        return phrase

        # chiede ingredienti pozione
        # TODO
        # aggiungere altre frasi

    @classmethod
    def ask_ingredients(self, potion):
        lexicon = Lexicon.getDefaultLexicon()
        realiser = Realiser(lexicon)
        nlgFactory = NLGFactory(lexicon)
        p = nlgFactory.createClause(
            f"Can you tell me the ingredients of {potion}")
        phrase = realiser.realiseSentence(p)
        return phrase


# test = Nlg()
# # # print(test.get_comment("neutral"))
# # # ingredient = "moon water"
# # # potion = "Amortentia"
# t = "sadasads sadasddas"
# print(f"backup_question: {test.backup_question(t)}")

# # print(test.get_comment("good_answer"))
# # # print(f" greeting {test.greetings()}")
# # print(f"ask ingr {test.ask_ingredients()}")
# print(f"generate_tricky_question  {test.generate_tricky_question()}")
# print(f"grade response: {test.grade_comment(18)}")
# print(f"Missing ingr: {test.missing_ingredients()}")
