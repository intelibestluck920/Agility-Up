import openai
import re
from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch

openai.api_key = "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"
model = SentenceTransformer('all-mpnet-base-v2')

'''post rework 9-11-22'''

def gpt3_data_analysis(text):
  response = openai.Completion.create(
    model="text-davinci-002",
    prompt=f"Summarize the reviews.\nInclude summary of every point.\nText:\n{text}\n\nSummary:\n",
    temperature=0.3,
    max_tokens=256,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  return response.choices[0].text.strip()



'''post rework tweaks 28-10-22'''



def generate_intent(sentence):
  response = openai.Completion.create(
    model="text-davinci-002",
    prompt=f"Extract key phrases from text.\nInclude only key phrases that have positive or negative sentimental meaning.\n\n###\n\nText: I hate Charles. His attitude towards me is really bad. Sundar Pichai said in his keynote that users love their new Android phones.\nKey phrases:\n- Hate Charles\n- Bad attitude\n- Love new android phones\n\n###\n\nText:{sentence}\nKey phrases:\n",
    temperature=0,
    max_tokens=32,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  res = response.choices[0].text.lower()
  topic_list = res.split("\n")
  new_topic_list = []
  for topic in topic_list:
    if len(topic)>3:
      new_topic_list.append(re.sub('[^A-Za-z ]+', '', topic).strip())
  return new_topic_list


def check_similarity(topic_list, topics):
    corpus_embedding = model.encode(topics)
    topic_embedding = model.encode(topic_list)
    scores = util.dot_score(corpus_embedding, topic_embedding)
    top_results = torch.topk(scores, k=1)
    corpus_index = 0
    best_index = []
    for score, idx in zip(top_results[0], top_results[1]):
        if score > 0.6:
            # print (f"found similar topic: {topic_list[idx]}")
            best_index.append((score, corpus_index, idx))
        corpus_index += 1
    if len(best_index) == 0:
        # If not found, add the best score topic to list
        score_idx = np.argmax(top_results[0])
        topic_index = top_results[1][score_idx]
        topics.append(topic_list[topic_index])
        response = {
            'new': True,
            'topics': topic_list[topic_index]
        }
    else:
        # If found, show the best score topic
        best_score_idx = np.argmax(best_index, axis=0)[0]
        response = {
            'new': False,
            'topics': topics[best_index[best_score_idx][1]]
        }
    return response

'''post rework tweaks 28-10-22'''

def check_summary_similarity(summary_list):
  unique_sentences = []
  for i in range (0, len(summary_list)-1):
    corpus_embedding = model.encode(summary_list[i+1:])
    sentence_embedding = model.encode(summary_list[i])
    scores = util.dot_score(corpus_embedding, sentence_embedding)
    if all(x < 0.8 for x in scores[0]):
      unique_sentences.append(summary_list[i])
  # Last sentence
  corpus_embedding = model.encode(summary_list[:-1])
  sentence_embedding = model.encode(summary_list[len(summary_list)-1])
  scores = util.dot_score(corpus_embedding, sentence_embedding)
  if all(x < 0.8 for x in scores[0]):
    unique_sentences.append(summary_list[len(summary_list)-1])
  return unique_sentences


def generate_summary(topics_list):
  keywords = ', '.join(topics_list)
  response = openai.Completion.create(
    model="text-davinci-002",
    prompt=f'List in bullets the summary of the negative reviews for the company for each keyword\nIf there is one keyword, give one sentence\n\n###\n\nKeywords: apples, team lead attitude, coffee taste\nSummary:\n- Some people did not like apples.\n- Some employees did not like team lead\'s attitude.\n- Some reviewers complained about coffee taste\n\n###\n\nKeywords: {keywords}\nSummary:\n',
    temperature=0.2,
    max_tokens=128,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  summary = response.choices[0].text.strip()
  summary_split = summary.split('\n')
  if (len(summary_split) > 1):
    unique_sentences = check_summary_similarity(summary_split)
    return '\n'.join(unique_sentences)
  else:
    return summary


''' new methods  28-10-22'''



def generate_negative_experiences(topics_list):
  keywords = ', '.join(topics_list)
  response = openai.Completion.create(
    model="text-davinci-002",
    prompt=f'List in bullets only the negative analysis for the company for each key phrase\nIf there is one key phrase, give one sentence\n\n###\n\nKey phrases: love apples, team lead attitude, coffee taste\nSummary:\n- Some people did not love apples.\n- Some employees did not like team lead\'s attitude.\n- Some reviewers complained about coffee taste\n\n###\n\nKey phrases: {keywords}\nSummary:\n',
    temperature=0.2,
    max_tokens=128,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  summary = response.choices[0].text.strip()
  summary_split = summary.split('\n')
  if (len(summary_split) > 1):
    unique_sentences = check_summary_similarity(summary_split)
    return '\n'.join(unique_sentences)
  else:
    return summary

def generate_positive_experiences(topics_list):
  keywords = ', '.join(topics_list)
  response = openai.Completion.create(
    model="text-davinci-002",
    prompt=f'List in bullets only the postive analysis for the company for each key phrase\nIf there is one key phrase, give one sentence\n\n###\n\nKey phrases: apples, team lead attitude, coffee taste\nSummary:\n- Some people liked apples.\n- Some employees appreciated team lead\'s attitude.\n- Some reviewers loved coffee taste\n\n###\n\nKey phrases: {keywords}\nSummary:\n',
    temperature=0.2,
    max_tokens=128,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
  )
  summary = response.choices[0].text.strip()
  summary_split = summary.split('\n')
  if (len(summary_split) > 1):
    unique_sentences = check_summary_similarity(summary_split)
    return '\n'.join(unique_sentences)
  else:
    return summary