# Instagram report

A plain HTML page that reports the club's Instagram numbers for the committee
and for sponsors. It is served by GitHub Pages at
https://risaac09.github.io/ritc-brand/report/ and has no build step, no
framework, and no outside service. The page reads the JSON files in `data/`
and prints them.

## The rule this page keeps

Every figure states the dates it covers, and figures from different date
ranges are never added, divided or compared with each other. A 30-day
Insights number and a follower count taken on one day go side by side, each
with its own date, and nothing is derived from the pair. If you add a figure,
give it a window line too.

## Monthly update

Do this before the first-Monday committee meeting.

1. **Insights, by hand.** On the club account, open Professional dashboard,
   then Insights, set to "Last 30 days". Copy the numbers into
   `data/insights.json`, and set `read_on` to the day you read them. The page
   says "as shown when read on" because Instagram does not print the exact
   start and end dates of its 30-day window. Copy
   the most-active-times bars into `data/active_hours.json`, and set
   `read_on`.
2. **Public counts.** Add a row to the top of `data/profile.json` with the
   day's followers, following and post count. Keep the old rows, because they
   are the follower history. In `data/posts.json`, update likes, comments and
   plays, and add any new post with `mentions_on` and `mentions_runnewport`
   set from its tags. You can copy these by hand from the profile or pull them
   with a scraper. Say which in the log.
3. **Log it.** Add an entry to `data/update_log.json`: the date, what you
   updated, your name, and how you did it. Set `next_due` to the next
   first-Monday meeting.
4. Commit with a message that says what changed, and push. Pages republishes
   within a few minutes.

The commit history of `report/data/` is the full record of who changed what
and when.

## Field notes

- `posts.json` `likes` is `null` when the poster hid likes. The page shows
  "hidden".
- `plays` is reel plays only. Carousels and photos have `null`.
- `collab` is true when the post lives on the club grid but another account
  posted it. `owner` names organisations (Run Newport, Fundati, NBC Sports
  Boston) but is `member` for an athlete's own account, and titles carry no
  athlete names, per the repo rule on crediting people only with permission.
- Keep every post on the grid dated Oct 1, 2025 or later. The page prints the
  date range it finds; it cannot tell you a post is missing.
