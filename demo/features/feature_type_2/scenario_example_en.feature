@feature_type_2 @severity.normal
Feature: What can assistant do
# created by admin | last edited by admin, 10-10-2021 10:00:00 | published by admin

Background:
  Given I am bank client

Scenario: User asks in a voice "what can assistant do" and gets an answer
  When I say "What can you do?"
  Then bot responds "This is what I can do"
  And bot shows widget
