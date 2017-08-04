#Myles' Keybaord Prediction System
#UD CISC882 - Dr. Kathleen Mccoy -  NLP Assignment #2 - Due 11/1/16
#Code written entirely by Myles Johnson-Gray (mjgray@udel.edu)

#This system is a predictor using character bigrams and other features to generate predictions for a dynamic keyboard.
#The system splits the input corpus into two sets and performs training and testing on the respective sets.
#The program outputs the test set and predictions to a file to be used by Amy Siu's GetScanTime.pl file.
#The performance of the predictor model is to be governed by the total scan time output from GetScanTime.pl (*not in this program*).
#-----------------------------------------------------------------------------------------------------------------------
#IMPORTS
from random import randint #to generate random integers
#-----------------------------------------------------------------------------------------------------------------------

#MAIN EXECUTION!!!!!!

#INITIALIZATION (Initialize important variables and open files for reading and writing.)

content = "" #to hold the input corpus (in string format)

#Read in the corpus file (subset of Brown corpus) by line:
with open("brown_nolines2.txt") as f:
     split_content = f.read().splitlines()

#Append the list containing corpus lines to content (convert to string format).
for i in range(0, len(split_content)):
    content = content + split_content[i]

print(content)

#Open the prediction/test_set files for writing. These output files necessary for Amy Siu's GetScanTime.pl file.
pred_file = open("predict_keyboard.txt", "w", newline="\n")
test_file = open("test_set.txt", "w")

t=content

#Split corpus into train set and test set.
fold_size = 10
#Example: To perform 10-fold validation: Run program 10 times and average the scan times for the 10 sets of test_set.txt and predict_keyboard.txt.
t = t.lower() #only use lower case characters
random_int = randint(0, len(t) - (int(len(t)/fold_size)+1)) #get a random index in the corpus
test_set = t[random_int:random_int+int(len(t)/fold_size)] #the test set is 1/fold_size of the corpus
train_set = t.replace(t[random_int:random_int+int(len(t)/fold_size)], "") #the train set is the remainder

#Write the testing set to test_set.txt.
test_file.write(test_set)

#Store all the observed characters in the training set in t_chars list.
t_chars = []
for i in range(0, len(train_set)):
    if train_set[i] not in t_chars:
        t_chars.append(train_set[i])

#-----------------------------------------------------------------------------------------------------------------------

train_set = content #FOR FINAL TESTING

with open("WenhaoWu-2.txt") as f2:
    test_set = f2.read()

#TRAINING (Create predictor model using observed bigram frequencies from the training file.)

#Initialize variables for training.
bigram = [] #hold list of observed bigrams
gram_prob = [] #hold probability of bigrams (index matches bigram[])

#Contains the top 6 most frequent characters in English. Used to handle <UNK> characters and to fill an unfinished prediction window.
top_letters = ("e", "t", "a", "o", "i", "n")

#Contains the top 30 most frequent bigrams in English (http://norvig.com/mayzner.html) to supplement observed frequencies.
top_bigrams = ["le", "io", "ou", "as", "ha", "se", "ng", "nt", "to", "st", "ar", "al", "it", "is", "es", "of", "te", "or", "es", "ti", "nd",
               "en", "at", "on", "or", "an", "er", "in", "he", "th"]

#Go through the training sequence and find all bigrams along with their probabilities
from collections import Counter
bigrams = Counter(x+y for x, y in zip(*[train_set[i:] for i in range(2)]))
for set, count in bigrams.most_common(): # set = all observed bigrams, count = # of occurrences
    if set[1] is not " ": #don't include bigrams ending with a space because we never want to predict a space...

        if set in top_bigrams: #if the bigram is a top 30 bigram in English, give it's calculated frequency an appropriate boost
            #Add bigram string and probabilities to their respective lists.
            bigram.append(set)
            gram_prob.append((count / train_set.count(set[0])) + (.1 * ((top_bigrams.index(set) + 1) / 15)))
            #print(set, count, (count / train_set.count(set[0])) + (.1 * ((top_bigrams.index(set) + 1) / 15)))

        else: #if bigram is not a top 30 bigram, just calculate it's frequency
            #Add bigram string and probabilities to their respective lists.
            bigram.append(set)
            gram_prob.append(count/train_set.count(set[0]))
            #print(set, count, count/train_set.count(set[0]))
print("---------------------------------------------------------------------------------------------------------------")

#-----------------------------------------------------------------------------------------------------------------------

#TESTING (Output predictions for the test set using the trained predictor model to predict_keyboard.txt.)
print("[Test_char][Predictions]") #format for console output
window_size = 5 #the number of predictions to output for each training character

print("".join(top_letters[0:window_size]))
pred_file.write("".join(top_letters[0:window_size]) + "\n") #always make the first prediction the top "window_size" occurring chars in English

#Go through the test sequence char-by-char (starting at the second character) and get predictions.
for i in range(1, len(test_set)):
    solutions = [] #holds the index of bigrams whose first char matches the current test char
    prediction = "" #holds the prediction string to be output to predict_keyboard.txt

    #If we are encountering an <UNKNOWN> character...   **This eliminates the need for smoothing**
    if test_set[i-1] not in t_chars:
        print("[UNK] " + "".join(top_letters[0:window_size]))
        pred_file.write("".join(top_letters[0:window_size]) + "\n") #simply output the top "window_size" occurring chars in English
    else: #otherwise...
        #Iterate through the observed bigrams.
        for k in range(0, len(bigram)):
            if test_set[i-1] is bigram[k][0]: #the test sequence char matches the first char in the bigram (A match!)
                solutions.append(k) #append the index of the bigram to the solutions list

        #Get "window_size" number of predictions
        for j in range(0, window_size):
            max_score = 0 #best probability so far
            best_solution = 0 # best bigram index so far
            #For each found solution...
            for item in solutions:
                if gram_prob[item] > max_score: #if a new highest probability is found, reassign max_score and best_solution
                    max_score = gram_prob[item]
                    best_solution = item

            if bigram[best_solution][1] not in prediction: #if the best solution is not already in the prediction string...
                prediction = prediction + bigram[best_solution][1] #append the prediction to the prediction string
                if best_solution in solutions: solutions.remove(best_solution) #remove the best solution from the solution list

        #If the window still isn't filled (possibly due to lack of observations)...
        while(len(prediction) < window_size):
            #Go through the top 6 English characters and fill the window.
            for m in range(0, len(top_letters)):
                if len(prediction) >= window_size: #break if the prediction length reaches the window size
                    break
                if top_letters[m] not in prediction: #add a top 6 character if it isn't already in the prediction
                    prediction = prediction + top_letters[m]

        print("[" + test_set[i - 1] + "] [" + prediction + "]") #output test char and predictions to console
        pred_file.write(prediction + "\n") #output the prediction to predict_keyboard.txt

#Close any opened files.
pred_file.close()
test_file.close()
f.close()
print("---------------------------------------------------------------------------------------------------------------")
print("DONE")
