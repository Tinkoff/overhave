@feature_type_2
Feature: What can assistant do

Background:
  Given I am bank client

Scenario: User asks in a voice "what can assistant do" and gets an answer
  When I say "What can you do?"
  Then bot responds "This is what I can do"
  And bot shows widget
