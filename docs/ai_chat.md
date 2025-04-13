Let's pair program!

Today we'll be building the following:

A Venmo auto-request tool.

Every month I have a list of friends who owe me money.

That list, along with all their info like names, amounts owed, and for what, Venmo ID, etc., will all be saved in a Google Sheets doc.

We should read from that, then use the Venmo API to request for each row in that sheet.

This should happen on the 1st of the month at 10 AM.

I would like to receive email reports summarizing the requests sent.

If there are ever any errors, I want to receive an email about the error.

I want to build this using Python 3.12 or 3.13 so we can utilize the latest features. I'm happy to use any popular Python libraries that can make our code easier.

I want to unit test everything using pytest. This is very important. Our tests should represent what each unit of code is responsible for.

When we build this, I want to use dependency injection to make the code less coupled and easier to test.

I want to use GitHub Actions to build, lint, and test the code on all commits to main and any PRs.

I want to use Docker.

For Python, we should use uv for dependency management and ruff for linting the code.

I'm not sure how to structure this so the job runs on the beginning of every month. Where should it be hosted? Do I just deploy my Docker container and the cron feature is something that's a part of that container? Let's lightly touch on what our options are here.
