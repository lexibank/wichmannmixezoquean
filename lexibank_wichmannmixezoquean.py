# coding=utf-8
from __future__ import unicode_literals, print_function
import re

import attr
from clldutils.misc import slug

from pylexibank.dataset import Dataset, Metadata, Language
from pylexibank.lingpy_util import getEvoBibAsBibtex


@attr.s
class MixeZoqueanLanguage(Language):
    source = attr.ib(default=None)


class MixeZoquean(Dataset):
    metadata = Metadata(
        title="Lexicostatistical Dataset of Mixe-Zoquean",
        citation="Cysouw, Michael and Søren Wichmann and David Kamholz. 2006. "
        "A critique of the separation base method for genealogical subgrouping, with "
        "data from Mixe-Zoquean. Journal of Quantitative Linguistics 13. 225-26.",
        license="https://creativecommons.org/licenses/by-nc/4.0/",
        conceptlist="Cysouw-2006-110")
    language_class = MixeZoqueanLanguage

    def cmd_download(self, **kw):
        sources = set(
            [l['SOURCE'] for l in self.languages if l['SOURCE']] + ['Cysouw2006a'])
        self.raw.write('sources.bib', getEvoBibAsBibtex(*sources, **kw))

    def cmd_install(self, **kw):
        languages = {
            l['ABBREVIATION']: dict(
                ID=l['ABBREVIATION'],
                glottocode=l['GLOTTOCODE'],
                name=l['NAME'],
                source=l['SOURCE'])
            for l in self.languages}
        concept_map = {
            c.english: c.concepticon_id for c in self.conceptlist.concepts.values()}

        cogidx = 1
        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())
            header = None
            for i, (row1, row2) in enumerate(
                    zip(self.raw.read_tsv('Wordlist.txt'),
                        self.raw.read_tsv('Cognates.txt'))):
                if i == 0:
                    header = row1[1:]
                else:
                    concept = re.split(' [-—–]', row1[0])[0]
                    ds.add_concept(
                        ID=concept, gloss=concept, conceptset=concept_map[concept])
                    for abb, word, cog in zip(header, row1[1:], row2[1:]):
                        if word.strip() and word.strip() != '?':
                            if cog.strip().lower() != 'na':
                                cogid = slug(concept) + '-' + cog
                            else:
                                cogid = str(cogidx)
                                cogidx += 1

                            ds.add_language(**languages[abb])
                            for row in ds.add_lexemes(
                                Language_ID=abb,
                                Parameter_ID=concept,
                                Value=word,
                                Source=[languages[abb]['source']],
                                Cognacy=cogid,
                            ):
                                ds.add_cognate(
                                    lexeme=row,
                                    Cognate_set_ID=cogid,
                                    Cognate_source='Cysouw2006a')
