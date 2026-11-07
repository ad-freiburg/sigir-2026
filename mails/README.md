# Mails sent by the SIGIR 2026 program chairs

One file per mail campaign, in the input format of `ortler mail`
(https://github.com/ad-freiburg/ortler): a few header lines, a blank line,
then the body in Markdown. The file name starts with the date on which the
mail was sent.

The `# Query:` line points to the SPARQL query that computed the list of
recipients, in `../queries/mails/`. Columns of the query result can be used
as `{{placeholders}}` in the subject and body; `{{name}}`,
`{{firstname_or_fullname}}`, and the like are filled from the profile of
the recipient.

The `To:` lines with the actual recipients have been removed, as well as
all personal names except those of the program chairs.

## Profiles of PC and SPC members (January 2 to 3)

- [`2026-01-02_PC_add_DBLP.txt`](2026-01-02_PC_add_DBLP.txt): PC members, add your DBLP link and import your publications.
- [`2026-01-02_SPC_add_DBLP.txt`](2026-01-02_SPC_add_DBLP.txt): same for SPCs.
- [`2026-01-02_SPC_add_Profile.txt`](2026-01-02_SPC_add_Profile.txt): SPCs without an OpenReview profile, create one.
- [`2026-01-03_PC_add_Profile.txt`](2026-01-03_PC_add_Profile.txt) \[[query](../queries/mails/2026-01-03_PC_add_Profile.sparql)\]: same for PC members.

## Author-nominated reviewers (January 7 to 23)

Each submission had to nominate one of its authors as reviewer.

- [`2026-01-07_author_reviewer_for_multiple_papers.txt`](2026-01-07_author_reviewer_for_multiple_papers.txt) \[[query](../queries/mails/2026-01-07_author_reviewer_for_multiple_papers.sparql)\]: nominated for several submissions, please change that.
- [`2026-01-10_author_reviewer_for_multiple_papers.txt`](2026-01-10_author_reviewer_for_multiple_papers.txt) \[[query](../queries/mails/2026-01-10_author_reviewer_for_multiple_papers.sparql)\]: same, second round.
- [`2026-01-14_author_reviewer_for_multiple_papers.txt`](2026-01-14_author_reviewer_for_multiple_papers.txt) \[[query](../queries/mails/2026-01-14_author_reviewer_for_multiple_papers.sparql)\]: same, third round.
- [`2026-01-15_author_reviewer_for_multiple_papers.txt`](2026-01-15_author_reviewer_for_multiple_papers.txt) \[[query](../queries/mails/2026-01-15_author_reviewer_for_multiple_papers.sparql)\]: same, fourth round.
- [`2026-01-17_author_reviewer_for_multiple_papers.txt`](2026-01-17_author_reviewer_for_multiple_papers.txt) \[[query](../queries/mails/2026-01-17_author_reviewer_for_multiple_papers.sparql)\]: same, fifth round.
- [`2026-01-18_author_reviewer_for_multiple_papers.txt`](2026-01-18_author_reviewer_for_multiple_papers.txt) \[[query](../queries/mails/2026-01-18_author_reviewer_for_multiple_papers.sparql)\]: same, marked urgent.
- [`2026-01-15_author_reviewer_not_author.txt`](2026-01-15_author_reviewer_not_author.txt) \[[query](../queries/mails/2026-01-15_author_reviewer_not_author.sparql)\]: the nominated reviewer is not an author of the submission.
- [`2026-01-17_author_reviewer_not_author.txt`](2026-01-17_author_reviewer_not_author.txt) \[[query](../queries/mails/2026-01-17_author_reviewer_not_author.sparql)\]: same, second round.
- [`2026-01-18_author_reviewer_not_author.txt`](2026-01-18_author_reviewer_not_author.txt) \[[query](../queries/mails/2026-01-18_author_reviewer_not_author.sparql)\]: same, marked urgent.
- [`2026-01-23_author_reviewer_not_author_final.txt`](2026-01-23_author_reviewer_not_author_final.txt) \[[query](../queries/mails/2026-01-23_author_reviewer_not_author_final.sparql)\]: same, last call before desk rejection.

## Author profiles and DBLP (January 15 to 27)

Complete profiles with all publications are what OpenReview's conflict-of-interest detection relies on. See also the stage `registration-dblp-and-imported-publications.json` in `../stages/`.

- [`2026-01-15_authors_no_dblp_profile.txt`](2026-01-15_authors_no_dblp_profile.txt) \[[query](../queries/mails/2026-01-15_authors_no_dblp_profile.sparql)\]: authors without a DBLP URL in their profile.
- [`2026-01-15_authors_import_your_publications.txt`](2026-01-15_authors_import_your_publications.txt) \[[query](../queries/mails/2026-01-15_authors_import_your_publications.sparql)\]: authors with fewer publications in OpenReview than on DBLP.
- [`2026-01-21_many_coauthors_only_in_dblp.txt`](2026-01-21_many_coauthors_only_in_dblp.txt) \[[query](../queries/mails/2026-01-21_many_coauthors_only_in_dblp.sparql)\]: authors whose DBLP co-authors are largely missing from their OpenReview publications, action required.
- [`2026-01-21_no_dblp_profile.txt`](2026-01-21_no_dblp_profile.txt): same for an explicit list of authors without a DBLP URL.
- [`2026-01-21_profile_inactive.txt`](2026-01-21_profile_inactive.txt) \[[query](../queries/mails/2026-01-21_profile_inactive.sparql)\]: authors whose OpenReview profile is inactive.
- [`2026-01-22_no_dblp_certify_imported_publications_one_publication.txt`](2026-01-22_no_dblp_certify_imported_publications_one_publication.txt) \[[query](../queries/mails/2026-01-22_no_dblp_certify_imported_publications_one_publication.sparql)\]: fill out the "DBLP and Imported Publications" task; authors without DBLP URL and a single publication in their profile.
- [`2026-01-22_no_dblp_certify_imported_publications_ten_or_less_publications.txt`](2026-01-22_no_dblp_certify_imported_publications_ten_or_less_publications.txt) \[[query](../queries/mails/2026-01-22_no_dblp_certify_imported_publications_ten_or_less_publications.sparql)\]: same text, authors with 2 to 10 publications.
- [`2026-01-22_no_dblp_certify_imported_publications_all.txt`](2026-01-22_no_dblp_certify_imported_publications_all.txt) \[[query](../queries/mails/2026-01-22_no_dblp_certify_imported_publications_all.sparql)\]: same text as final call, authors with 10 or more publications.
- [`2026-01-23_no_dblp_certify_imported_publications_all_again.txt`](2026-01-23_no_dblp_certify_imported_publications_all_again.txt) \[[query](../queries/mails/2026-01-23_no_dblp_certify_imported_publications_all_again.sparql)\]: final call with step-by-step instructions.
- [`2026-01-23_no_dblp_certify_imported_publications_single_author.txt`](2026-01-23_no_dblp_certify_imported_publications_single_author.txt) \[[query](../queries/mails/2026-01-23_no_dblp_certify_imported_publications_single_author.sparql)\]: same for authors with few prior publications.
- [`2026-01-23_no_dblp_certify_imported_publications_final.txt`](2026-01-23_no_dblp_certify_imported_publications_final.txt) \[[query](../queries/mails/2026-01-23_no_dblp_certify_imported_publications_final.sparql)\]: to the co-authors, last warning that the submission will be desk-rejected.
- [`2026-01-25_desk_reject_submissions_with_many_incomplete_profiles.txt`](2026-01-25_desk_reject_submissions_with_many_incomplete_profiles.txt) \[[query](../queries/mails/2026-01-25_desk_reject_submissions_with_many_incomplete_profiles.sparql)\]: notification of desk rejection because of incomplete profiles.
- [`2026-01-27_desk_reject_submissions_with_many_incomplete_profiles.txt`](2026-01-27_desk_reject_submissions_with_many_incomplete_profiles.txt) \[[query](../queries/mails/2026-01-27_desk_reject_submissions_with_many_incomplete_profiles.sparql)\]: same, second batch.

## Start of reviewing (January 30 to February 7)

- [`2026-01-30_info_to_everyone.txt`](2026-01-30_info_to_everyone.txt): announcement of the Slack channel for the track.
- [`2026-01-31_assignment_quality_reminder.txt`](2026-01-31_assignment_quality_reminder.txt) \[[query](../queries/mails/2026-01-31_assignment_quality_reminder.sparql)\]: SPCs and ACs, reminder to fill out the assignment-quality survey.

## Review deadline (February 12 to 21)

The deadline was February 17 AoE.

- [`2026-02-12_pc_reminder_1a.txt`](2026-02-12_pc_reminder_1a.txt) \[[query](../queries/mails/2026-02-12_pc_reminder_1a.sparql)\]: start your first review today.
- [`2026-02-12_pc_reminder_1b.txt`](2026-02-12_pc_reminder_1b.txt) \[[query](../queries/mails/2026-02-12_pc_reminder_1b.sparql)\]: one review done, start your second today.
- [`2026-02-12_pc_reminder_2.txt`](2026-02-12_pc_reminder_2.txt) \[[query](../queries/mails/2026-02-12_pc_reminder_2.sparql)\]: two days left, no reviews yet.
- [`2026-02-12_pc_reminder_3.txt`](2026-02-12_pc_reminder_3.txt) \[[query](../queries/mails/2026-02-12_pc_reminder_3.sparql)\]: hours left, no reviews yet, extension offered.
- [`2026-02-12_pc_reminder_4.txt`](2026-02-12_pc_reminder_4.txt) \[[query](../queries/mails/2026-02-12_pc_reminder_4.sparql)\]: deadline passed, several reviews missing.
- [`2026-02-19_pc_reminder_5.txt`](2026-02-19_pc_reminder_5.txt) \[[query](../queries/mails/2026-02-19_pc_reminder_5.sparql)\]: deadline passed, one review missing.
- [`2026-02-21_emergency_reviewers_1.txt`](2026-02-21_emergency_reviewers_1.txt) \[[query](../queries/mails/2026-02-21_emergency_reviewers_1.sparql)\]: additional assignment for a submission with too few reviews, due February 27.
- [`2026-02-21_emergency_reviewers_2.txt`](2026-02-21_emergency_reviewers_2.txt) \[[query](../queries/mails/2026-02-21_emergency_reviewers_2.sparql)\]: same, second batch.
- [`2026-02-21_emergency_reviewers_3.txt`](2026-02-21_emergency_reviewers_3.txt) \[[query](../queries/mails/2026-02-21_emergency_reviewers_3.sparql)\]: same, third batch, due February 28.
- [`2026-02-21_spc_missing_reviews.txt`](2026-02-21_spc_missing_reviews.txt) \[[query](../queries/mails/2026-02-21_spc_missing_reviews.sparql)\]: SPCs with missing reviews on their submissions, please chase the reviewers.
- [`2026-02-21_spc_no_missing_reviews.txt`](2026-02-21_spc_no_missing_reviews.txt) \[[query](../queries/mails/2026-02-21_spc_no_missing_reviews.sparql)\]: SPCs with all reviews in, status update.

## Discussion phase (February 22 to March 9)

The discussion phase ran from February 22 to March 10 AoE.

- [`2026-02-22_discussion_phase_pc_1.txt`](2026-02-22_discussion_phase_pc_1.txt) \[[query](../queries/mails/2026-02-22_discussion_phase_pc_1.sparql)\]: PC members, what to do in the discussion phase.
- [`2026-02-22_discussion_phase_pc_2.txt`](2026-02-22_discussion_phase_pc_2.txt) \[[query](../queries/mails/2026-02-22_discussion_phase_pc_2.sparql)\]: same, for PC members with a pending emergency review.
- [`2026-02-22_discussion_phase_pc_3.txt`](2026-02-22_discussion_phase_pc_3.txt) \[[query](../queries/mails/2026-02-22_discussion_phase_pc_3.sparql)\]: same, for PC members with reviews still missing.
- [`2026-02-22_discussion_phase_spc_1.txt`](2026-02-22_discussion_phase_spc_1.txt) \[[query](../queries/mails/2026-02-22_discussion_phase_spc_1.sparql)\]: SPCs, how to lead the discussions and write the meta-review.
- [`2026-03-01_discussion_phase_spc_2a.txt`](2026-03-01_discussion_phase_spc_2a.txt) \[[query](../queries/mails/2026-03-01_discussion_phase_spc_2a.sparql)\]: one week in, no discussion started yet.
- [`2026-03-01_discussion_phase_spc_2b.txt`](2026-03-01_discussion_phase_spc_2b.txt) \[[query](../queries/mails/2026-03-01_discussion_phase_spc_2b.sparql)\]: one week in, some discussions started.
- [`2026-03-01_discussion_phase_spc_2c.txt`](2026-03-01_discussion_phase_spc_2c.txt) \[[query](../queries/mails/2026-03-01_discussion_phase_spc_2c.sparql)\]: one week in, all discussions started, thank you.
- [`2026-03-05_discussion_phase_spc_3a.txt`](2026-03-05_discussion_phase_spc_3a.txt) \[[query](../queries/mails/2026-03-05_discussion_phase_spc_3a.sparql)\]: still no discussion started, five days left.
- [`2026-03-05_discussion_phase_spc_3b.txt`](2026-03-05_discussion_phase_spc_3b.txt) \[[query](../queries/mails/2026-03-05_discussion_phase_spc_3b.sparql)\]: please start the remaining discussions.
- [`2026-03-07_discussion_phase_spc_4a.txt`](2026-03-07_discussion_phase_spc_4a.txt) \[[query](../queries/mails/2026-03-07_discussion_phase_spc_4a.sparql)\]: still no discussion started, urgent.
- [`2026-03-07_discussion_phase_spc_4b.txt`](2026-03-07_discussion_phase_spc_4b.txt) \[[query](../queries/mails/2026-03-07_discussion_phase_spc_4b.sparql)\]: please help chase reviewers who have not participated.
- [`2026-03-07_discussion_phase_missing_comments_pc_1a.txt`](2026-03-07_discussion_phase_missing_comments_pc_1a.txt) \[[query](../queries/mails/2026-03-07_discussion_phase_missing_comments_pc_1a.sparql)\]: PC members who have not participated in any discussion.
- [`2026-03-07_discussion_phase_missing_comments_pc_1b.txt`](2026-03-07_discussion_phase_missing_comments_pc_1b.txt) \[[query](../queries/mails/2026-03-07_discussion_phase_missing_comments_pc_1b.sparql)\]: PC members who have not participated in some discussions.
- [`2026-03-09_discussion_phase_spc_5a.txt`](2026-03-09_discussion_phase_spc_5a.txt) \[[query](../queries/mails/2026-03-09_discussion_phase_spc_5a.sparql)\]: still no discussion started, meta-reviews due tomorrow.

## Review ratings and meta-reviews (March 1 to 12)

Due March 10 AoE. See the stages `review-rating.json` and `meta-review.json` in `../stages/`.

- [`2026-03-01_review_rating_and_meta_review_spc_1.txt`](2026-03-01_review_rating_and_meta_review_spc_1.txt) \[[query](../queries/mails/2026-03-01_review_rating_and_meta_review_spc_1.sparql)\]: the forms are deployed, how to use them.
- [`2026-03-09_review_rating_and_meta_review_spc_2.txt`](2026-03-09_review_rating_and_meta_review_spc_2.txt) \[[query](../queries/mails/2026-03-09_review_rating_and_meta_review_spc_2.sparql)\]: one day left.
- [`2026-03-11_metareviews_spc_1a.txt`](2026-03-11_metareviews_spc_1a.txt) \[[query](../queries/mails/2026-03-11_metareviews_spc_1a.sparql)\]: hours left, some meta-reviews still missing.
- [`2026-03-11_metareviews_spc_1b.txt`](2026-03-11_metareviews_spc_1b.txt) \[[query](../queries/mails/2026-03-11_metareviews_spc_1b.sparql)\]: hours left, no meta-review submitted yet.
- [`2026-03-11_review_rating_variation.txt`](2026-03-11_review_rating_variation.txt) \[[query](../queries/mails/2026-03-11_review_rating_variation.sparql)\]: SPCs whose review ratings have very low variance, please check them.
- [`2026-03-12_metareviews_spc_2a.txt`](2026-03-12_metareviews_spc_2a.txt) \[[query](../queries/mails/2026-03-12_metareviews_spc_2a.sparql)\]: deadline passed, no meta-review received, urgent.

## Area chairs and decisions (March 8 to 23)

See the stage `decision-recommendation-ac.json` in `../stages/`.

- [`2026-03-08_status_quo_ac_1.txt`](2026-03-08_status_quo_ac_1.txt) \[[query](../queries/mails/2026-03-08_status_quo_ac_1.sparql)\]: the AC phase begins, what ACs do, with a table of their submissions.
- [`2026-03-09_status_quo_ac_2.txt`](2026-03-09_status_quo_ac_2.txt) \[[query](../queries/mails/2026-03-09_status_quo_ac_2.sparql)\]: updated table.
- [`2026-03-11_status_quo_ac_3.txt`](2026-03-11_status_quo_ac_3.txt) \[[query](../queries/mails/2026-03-11_status_quo_ac_3.sparql)\]: updated table, and how AI-generated reviews and meta-reviews are flagged.
- [`2026-03-15_status_quo_ac_4.txt`](2026-03-15_status_quo_ac_4.txt) \[[query](../queries/mails/2026-03-15_status_quo_ac_4.sparql)\]: missing meta-reviews, the meetings with the PC chairs, target acceptance rate, the Decision button.
- [`2026-03-16_ac_meetings.txt`](2026-03-16_ac_meetings.txt) \[[query](../queries/mails/2026-03-16_ac_meetings.sparql)\]: sign up for a 20-minute meeting with the PC chairs.
- [`2026-03-19_ac_decisions_1.txt`](2026-03-19_ac_decisions_1.txt) \[[query](../queries/mails/2026-03-19_ac_decisions_1.sparql)\]: fill out the Decision form for each submission.
- [`2026-03-20_ac_meetings_webpages.txt`](2026-03-20_ac_meetings_webpages.txt) \[[query](../queries/mails/2026-03-20_ac_meetings_webpages.sparql)\]: link to the live overview page of their submissions, the agenda for the meeting.
- [`2026-03-20_ac_meetings_mail_to_Hannah_Marc_Min.txt`](2026-03-20_ac_meetings_mail_to_Hannah_Marc_Min.txt) \[[query](../queries/mails/2026-03-20_ac_meetings_mail_to_Hannah_Marc_Min.sparql)\]: the same links, sent to the PC chairs themselves.
- [`2026-03-21_ac_meetings_mail_1.txt`](2026-03-21_ac_meetings_mail_1.txt) \[[query](../queries/mails/2026-03-21_ac_meetings_mail_1.sparql)\]: the meetings start, check your slot, table for the discussion.
- [`2026-03-23_ac_meetings_mail_2.txt`](2026-03-23_ac_meetings_mail_2.txt) \[[query](../queries/mails/2026-03-23_ac_meetings_mail_2.sparql)\]: fill out your Decision forms before the meeting.

## After the decisions (April 2 to May 7)

- [`2026-04-02_notification_accept.txt`](2026-04-02_notification_accept.txt) \[[query](../queries/mails/2026-04-02_notification_accept.sparql)\]: acceptance notification.
- [`2026-04-02_notification_accept_2.txt`](2026-04-02_notification_accept_2.txt) \[[query](../queries/mails/2026-04-02_notification_accept_2.sparql)\]: same, resent after duplicate mails.
- [`2026-04-02_notification_reject.txt`](2026-04-02_notification_reject.txt) \[[query](../queries/mails/2026-04-02_notification_reject.sparql)\]: rejection notification.
- [`2026-04-02_notification_reject_2.txt`](2026-04-02_notification_reject_2.txt) \[[query](../queries/mails/2026-04-02_notification_reject_2.sparql)\]: same, resent after duplicate mails.
- [`2026-04-12_author_feedback.txt`](2026-04-12_author_feedback.txt) \[[query](../queries/mails/2026-04-12_author_feedback.sparql)\]: authors, please rate your reviews, meta-review, and the process (see the author-feedback stages in `../stages/`).
- [`2026-04-27_assignment_quality.txt`](2026-04-27_assignment_quality.txt) \[[query](../queries/mails/2026-04-27_assignment_quality.sparql)\]: SPCs and ACs, results of the assignment-quality survey and thanks.
- [`2026-05-07_best_paper_award.txt`](2026-05-07_best_paper_award.txt): best paper award committee, shortlist and access to the reviews.
