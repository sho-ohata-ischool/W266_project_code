## This is a helper script to extract entities from the full text of the article
## Because the leading letters of the words are capitalized there is a need to
## make the leading letters of the words lower case, especially because capitalization
## impacts word embedding vectors.
## This code was inspired from: http://stackoverflow.com/questions/24398536/named-entity-recognition-with-regular-expression-nltk

import nltk

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
                
    return entity_names

def return_entity_list(full_text):
    entities = []

    for title in full_text:
        sentences = nltk.sent_tokenize(title)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

        for tree in chunked_sentences:
            entities.extend(extract_entity_names(tree))
            extract_entity_names(tree)

    entities = list(set(entities))

    entities_list_len2 = []

    for entity in entities:
        if len(entity.split()) > 1 and entity not in entities_list_len2:
            entities_list_len2.append(entity)
            
    return entities, entities_list_len2