import pathlib
import re

import attr
import pylexibank
from clldutils.misc import slug


@attr.s
class CustomLanguage(pylexibank.Language):
    Source = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = pathlib.Path(__file__).parent
    id = "wichmannmixezoquean"
    language_class = CustomLanguage

    def cmd_makecldf(self, args):
        languages = {
            l["ABBREVIATION"]: dict(
                ID=slug(l["ABBREVIATION"]),
                Glottocode=l["GLOTTOCODE"],
                Name=l["NAME"],
                Source=l["SOURCE"],
            )
            for l in self.languages
        }
        concepts = {c.english: c.concepticon_id for c in self.conceptlists[0].concepts.values()}

        cogidx = 1
        args.writer.add_sources()

        header = None
        for i, (row1, row2) in enumerate(
            zip(
                self.raw_dir.read_csv("Wordlist.txt", delimiter="\t"),
                self.raw_dir.read_csv("Cognates.txt", delimiter="\t"),
            )
        ):
            if i == 0:
                header = row1[1:]
            else:
                concept = re.split(" [-—–]", row1[0])[0]
                args.writer.add_concept(
                    ID=slug(concept), Concepticon_Gloss=concept, Concepticon_ID=concepts[concept]
                )
                for abb, word, cog in zip(header, row1[1:], row2[1:]):
                    if word.strip() and word.strip() != "?":
                        if cog.strip().lower() != "na":
                            cogid = slug(concept) + "-" + cog
                        else:
                            cogid = str(cogidx)
                            cogidx += 1

                        args.writer.add_language(**languages[abb])
                        for row in args.writer.add_lexemes(
                            Language_ID=slug(abb),
                            Parameter_ID=slug(concept),
                            Value=word,
                            Source=[languages[abb]["Source"]],
                            Cognacy=cogid,
                        ):
                            args.writer.add_cognate(
                                lexeme=row, Cognateset_ID=cogid, Source="Cysouw2006a"
                            )
