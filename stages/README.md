# OpenReview stages of the SIGIR 2026 Full Papers Track

A *stage* is OpenReview's term for a form together with the task of filling
it in: who is invited, when it opens and is due, who can read the result, and
which fields it asks for. Each file in this directory is one stage, in the
format in which it was deployed with `ortler`
(https://github.com/ad-freiburg/ortler). There are two formats:

- Compact format with `name`, `title`, `instructions`, `committee` or
  `invitees`, dates, and `content` (the fields); deployed with
  `ortler custom-stage FILE` (per-submission stages) or
  `ortler registration-stage FILE` (one form per person).
- Full OpenReview invitation format; deployed with `ortler review-stage FILE`
  or `ortler stage FILE`. The fields are under
  `edit.invitation.edit.note.content`; the dates under `edit.invitation`.
  A field given as `{"delete": true}` removes one of OpenReview's default
  fields (for example `title` and `review` in `review.json`).

All files were checked against the invitations live on OpenReview on
2026-11-07: the fields, options, descriptions and invitees match.

Role names follow SIGIR usage: PC members are OpenReview's `Reviewers`, SPCs
are `Area_Chairs`, and ACs are `Senior_Area_Chairs`. The file names use the
SIGIR names; the OpenReview names appear inside the files.

The stages are listed in the order in which they were used. For each: who
fills it in and when, what it asks, and what is particular about it. The
mails that announced the stage are linked.

## Before reviewing

### `registration-dblp-and-imported-publications.json`
Authors, January 21 to 24. One form per author. Asks whether the author has a
DBLP author page, a disambiguation page, or none (with the URL), and a
certification that all their publications have been imported into their
OpenReview profile. Complete profiles are what OpenReview's conflict-of-
interest detection relies on; submissions with many incomplete profiles
were desk-rejected.

Relevant mails:
[`2026-01-22_no_dblp_certify_imported_publications_one_publication.txt`](../mails/2026-01-22_no_dblp_certify_imported_publications_one_publication.txt) (authors without DBLP URL, one submission),
[`2026-01-22_no_dblp_certify_imported_publications_ten_or_less_publications.txt`](../mails/2026-01-22_no_dblp_certify_imported_publications_ten_or_less_publications.txt) (same, few publications),
[`2026-01-22_no_dblp_certify_imported_publications_all.txt`](../mails/2026-01-22_no_dblp_certify_imported_publications_all.txt) (final call),
[`2026-01-25_desk_reject_submissions_with_many_incomplete_profiles.txt`](../mails/2026-01-25_desk_reject_submissions_with_many_incomplete_profiles.txt) (desk rejection for incomplete profiles).

### `initial-check-spc.json`, `initial-check-ac.json`
SPCs and ACs, January 25 to 27, for each assigned submission. A quick
one-to-two-minute look with one answer: proceed to review, or desk-reject
for exceeding the page limit, missing anonymization, wrong formatting, being
off-topic, or another reason given in a comment. Both roles see the same
form; the two files differ only in the committee. The answers were the input
for the program chairs' desk-rejection decisions.

### `assignment-quality-feedback-spc.json`, `assignment-quality-feedback-ac.json`
SPCs and ACs, January 30 to February 18. One form per person: how many of
the assigned papers match their expertise (five levels), how this compares
to previous years, and free comments. Used to evaluate the automatic
assignment.

Relevant mails:
[`2026-01-31_assignment_quality_reminder.txt`](../mails/2026-01-31_assignment_quality_reminder.txt) (reminder),
[`2026-04-27_assignment_quality.txt`](../mails/2026-04-27_assignment_quality.txt) (results reported back).

## Reviewing and discussion

### `review.json`
PC members, January 29 to February 18 (deadline February 17 AoE), one review
per assigned submission. Fields: an acknowledgment of the responsible
reviewing policy from the call for papers; strengths; weaknesses; detailed
comments; an assessment of undue AI use in the submission; a rating from
+2 (accept) to -2 (reject) with a one-line definition per level; confidence
from 5 to 1; whether the review and the reviewer's identity may be passed on
to ICTIR or SIGIR-AP if the authors ask for it; whether the submission should
be considered for the best paper award; and confidential remarks for the
committee. The file also contains the process script that sends the
notification mails.

Relevant mails:
[`2026-02-12_pc_reminder_1a.txt`](../mails/2026-02-12_pc_reminder_1a.txt) (start your first review),
[`2026-02-12_pc_reminder_1b.txt`](../mails/2026-02-12_pc_reminder_1b.txt) (start your second review),
[`2026-02-12_pc_reminder_2.txt`](../mails/2026-02-12_pc_reminder_2.txt) (two days left, no reviews yet),
[`2026-02-12_pc_reminder_3.txt`](../mails/2026-02-12_pc_reminder_3.txt) (hours left, no reviews yet),
[`2026-02-12_pc_reminder_4.txt`](../mails/2026-02-12_pc_reminder_4.txt) (deadline passed, reviews missing),
[`2026-02-22_discussion_phase_pc_1.txt`](../mails/2026-02-22_discussion_phase_pc_1.txt) (what PC members do in the discussion phase).

### `review-rating.json`
SPCs, March 1 to 11, one rating per review on their submissions. A single
score from 5 (exemplary, very helpful) to 1 (very generic, superficial,
unfounded or short) plus an optional comment. The rating is visible to ACs
and program chairs only, never to reviewers or authors. It was the basis of
the best-reviewer awards and of the consequences for irresponsible
reviewing.

Relevant mails:
[`2026-03-01_review_rating_and_meta_review_spc_1.txt`](../mails/2026-03-01_review_rating_and_meta_review_spc_1.txt) (forms deployed, how to use them).

### `meta-review.json`
SPCs, March 1 to 11, one per submission. Fields: the meta-review (up to
5000 characters, Markdown), confidential remarks, a recommendation
(accept, reject, undecided), and confidence from 5 to 1. The invitation
was later extended so that ACs can also edit meta-reviews.

Relevant mails:
[`2026-02-22_discussion_phase_spc_1.txt`](../mails/2026-02-22_discussion_phase_spc_1.txt) (what SPCs do in the discussion phase),
[`2026-03-01_review_rating_and_meta_review_spc_1.txt`](../mails/2026-03-01_review_rating_and_meta_review_spc_1.txt) (forms deployed, how to use them),
[`2026-03-11_metareviews_spc_1a.txt`](../mails/2026-03-11_metareviews_spc_1a.txt) (deadline reminder).

## Decisions

### `decision-recommendation-ac.json`
ACs, March 19 to 28, one per submission. A decision (accept, reject, or
"discuss with PC chairs", to be used sparingly), a comment, and a rating of
the SPC's work on this submission from 5 (exemplary) to 1 (essentially
absent). The SPC ratings were the basis of the best-SPC awards. The
recommendations were discussed in the 20-minute meetings of the program
chairs with each AC.

Relevant mails:
[`2026-03-08_status_quo_ac_1.txt`](../mails/2026-03-08_status_quo_ac_1.txt) (what ACs do in the decision phase),
[`2026-03-19_ac_decisions_1.txt`](../mails/2026-03-19_ac_decisions_1.txt) (fill out the decision form).

## After notification

### `author-feedback-review.json`, `author-feedback-meta-review.json`, `author-feedback-process.json`
Authors, April 6 to 30. One form per review, per meta-review, and per
submission for the process as a whole. Each asks for a rating from 5 to 1
and an optional comment; the review and meta-review forms also ask whether
the feedback may be shared with the reviewer or SPC. The feedback is readable
by the program chairs only.

Relevant mails:
[`2026-04-12_author_feedback.txt`](../mails/2026-04-12_author_feedback.txt) (request for feedback).

## Not included

Stages that we used as OpenReview provides them (official comments in the
discussion phase, withdrawal, desk rejection, decision notification) are not
in this directory.
