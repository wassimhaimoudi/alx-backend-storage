-- Creates an index idx_name_first_score on table names and first letter of name
-- First letter of name must be indexed as well as the score

CREATE INDEX idx_name_first_score
ON names(name(1), score);
