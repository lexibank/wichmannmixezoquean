from pathlib import Path

import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import FormSpec
from pylexibank import Language as BaseLanguage


@attr.s
class CustomLanguage(BaseLanguage):
    Name = attr.ib(default=None)
    Abbreviation = attr.ib(default=None)
    Note = attr.ib(default=None)
    Source = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "wichmannmixezoquean"
    writer_options = dict(keep_languages=False, keep_parameters=False)

    language_class = CustomLanguage

    form_spec = FormSpec(brackets={"(": ")", "[": "]"}, separators=",~", missing_data=("?", "-"))

    def cmd_makecldf(self, args):
        args.writer.add_sources()

        languages = args.writer.add_languages(lookup_factory=lambda l: l["Abbreviation"])

        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id.split("-")[-1] + "_" + slug(c.english), lookup_factory="Name"
        )
        # add multiple forms
        concepts.update(
            {
                # note the mishmash of different dashes etc handled here.
                "hair - 1": "36_hair",
                "hair - 2": "36_hair",
                "see - 1": "72_see",
                "see - 2": "72_see",
                "stand - 1": "79_stand",
                "stand - 2": "79_stand",
                "stand -2": "79_stand",
                "walk/go - 1": "92_walkgo",
                "walk/go - 2": "92_walkgo",
                "worm - 1": "109_worm",
                "worm – 2": "109_worm",
                "worm - 2": "109_worm",
            }
        )

        sources = {l["Abbreviation"]: l["Source"] for l in self.languages}

        data = zip(
            self.raw_dir.read_csv("Wordlist.txt", delimiter="\t"),
            self.raw_dir.read_csv("Cognates.txt", delimiter="\t"),
        )

        cogidx = 1
        header = None
        for i, (row1, row2) in enumerate(data):
            if i == 0:
                header = row1[1:]
            else:
                concept_id = concepts[row1[0].strip()]
                for lang_abbrev, word, cog in zip(header, row1[1:], row2[1:]):
                    if word.strip():
                        if cog.strip().lower() != "na":
                            cogid = concept_id + "-" + cog
                        else:
                            cogid = str(cogidx)
                            cogidx += 1

                        for row in args.writer.add_forms_from_value(
                            Language_ID=languages[lang_abbrev],
                            Parameter_ID=concept_id,
                            Value=word,
                            Source=sources[lang_abbrev],
                            Cognacy=cogid,
                        ):
                            args.writer.add_cognate(
                                lexeme=row, Cognateset_ID=cogid, Source="Cysouw2006a"
                            )
