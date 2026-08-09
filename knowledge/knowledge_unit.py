class KnowledgeUnitGenerator:

    def __init__(self):
        self.knowledge_units = []

    ############################################################

    def generate(self, resume_json):

        self.knowledge_units = []

        for section, value in resume_json.items():

            if isinstance(value, list):

                self._process_list(section, value)

            elif isinstance(value, dict):

                self._process_dict(section, value)

        return self.knowledge_units

    ############################################################

    def _process_list(self, section, items):

        for item in items:

            if isinstance(item, dict):

                self.knowledge_units.append(
                    self._create_unit(section, item)
                )

    ############################################################

    def _process_dict(self, section, data):

        self.knowledge_units.append(
            self._create_unit(section, data)
        )

    ############################################################

    def _create_unit(self, section, data):

        return {

            "type": section,

            "title": self._get_title(data, section),

            "content": self._create_content(data)

        }

    ############################################################

    def _get_title(self, data, section):

        title_fields = [

            "project_name",

            "company_name",

            "institution",

            "degree",

            "name",

            "title"

        ]

        for field in title_fields:

            if field in data and data[field]:

                return data[field]

        return section.replace("_", " ").title()

    ############################################################

    def _create_content(self, data):

        lines = []

        for key, value in data.items():

            key = key.replace("_", " ").title()

            if value in ("", [], None):
                continue

            if isinstance(value, list):

                lines.append(f"{key}:")

                for item in value:

                    lines.append(f"- {item}")

                lines.append("")

            elif isinstance(value, dict):

                lines.append(f"{key}:")

                for k, v in value.items():

                    if isinstance(v, list):

                        lines.append(f"{k.replace('_',' ').title()}:")

                        for x in v:
                            lines.append(f"- {x}")

                    else:

                        lines.append(
                            f"{k.replace('_',' ').title()}: {v}"
                        )

                lines.append("")

            else:

                lines.append(f"{key}: {value}")

        return "\n".join(lines)