# Attribute Issues Plaything
_This documents the configuration files which allow the Plaything to be customised and notes how they relate to various useage scenarios._

Plaything name: attribute-issues

## Plaything Specification
Refer to the README in the pg_shared repository/folder for common elements; this README refers only to the elements which are specific to the Attribute Issues Plaything.
For the Attribute Issues Plaything, the Specifications folder is Config/attribute-issues.

Available views:
- "about" - available if there is an entry for "about" in the asset_map.
- "questionnaire"

### "detail"
The structure of the "detail" container comprises:
- attribute_scope [simple text]: Explains what kind of entity the attributes concern and outlines the process in which they are being used.
- key_question [simple text]: The headline question for the questionnaire, typically asking which attributes should NOT be used for a specified purpose.,
- issue_categories [a list of key-value structures]: Summarises the types of issue which might be assigned to an attribute. These should be ordered with the most important category first.
  - The structures take the form: {"code": "", "label": "", "summary": ""}. The __code__ is used internally and for logging and should not be changed once the plaything specification is in use. The __label__ is presented to users and may be changed without affecting the analysis of logged data (as it uses the code). The __summary__ element is optional; see below. There SHOULD be an entry with __code__ set to "" and with a suitable label for the no-category case, for example "No Issues"; this is used in the explanation provided following a questionnaire submission. This should be the last category in the list.
- response_type [simple text]: Determines what happens when the respondant submits their questionnaire responses. Valid values are "acknowledge" (provides no feedback) and "explain", which lists the responses and comments on the category assigned to each. Defaults to "explain".

### "asset_map"
The "about" entry is optional but if present should name a Markdown file for use on the "about" page. The markdown file should contain entries for all of the __issue_categories__ given above. 

The "attributes" entry must be present and names a CSV file with one row for each attribute under a heading line which gives the column names: "code", "label", "summary", "category", "explanation". The columns should be used as follows:
- code: a short identifier which is used internally and recorded in the response logging. The same identifier may be used in multiple specifications if desired. This may be helpful if, for example, the same questionnaire is presented to speakers of different languagues (prepare one specification for each), or the same set of attributes used in questionnaires which have different categories or key question. Using the same code makes it easier to analyse the resposne data across questionnaire groups. Recommended: make the code something you can recognise in the logged data.
- label: is the short name of the attribute as presented in the questionnaire.
- summary: is an extende explanation of the attribute. This may be omitted if respondants are already familiar with the attribute label.
- category: is the most important category of issue to which the attribute belongs. If there are no issues, this may be left blank.
- explanation: may be left blank unless there is something to say about how/why the attribute is associated with the category of issue assessed against the key question.

Recommended: use the specification id as the prefix of the asset file, adding something like "_issue_categories.md" or "_attributes.csv".

## Useage Scenarios, Configuration Options, and Suggestions
The plaything is designed to accommodate a range of scenarios according to the amount of pre-questionnaire information provided and of post-questionnaire explanation given. If pre-questionnaire information is to be provided, create the Markdown file for the "about" asset_map entry and include "about" in the __menu__ specification. Post-questionnaire explanation is controlled by the __response_type__ value. If this is "explain", the minimal explanation is simply a statement of the category of issue. This will be extended if: a) there are __summary__ entries in the __issue_categories__, or b) there is text in the "explanation" column of the CSV file for the given attribute.

### Suggestions
It is recommended to phrase the __key_question__ such that respondants identify problematical attributes, i.e. attributes which belong to at least one of the issue categories. The alternative would imply that the respondant should select useful attributes, which is something that can often only be determined by statistical analysis; the question would be asking respondants to guess!

# TODOs (Development)
Support two modes of response: a) checkbox for "there is an issue" (as now), and b) selector dropdown for category.