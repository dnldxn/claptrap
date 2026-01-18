# How to effectively use sub-agents in Copilot

- subreddit: r/GithubCopilot
- author: u/Cobuter_Man
- score: 57
- num_comments: 15
- url: https://i.redd.it/2pwqum25vhcg1.png
- permalink: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/

## Post body

Copilot's sub-agents are the best out there (IMO) currently. I use them for these three things mainly:

*  ad-hoc context-intensive tasks (research, data reading etc)
*  code review and audits against standards i set to the original calling agent
* debugging (but not doing the active debugging, rather reading debug logs, outputs etc - again to not burn context)

Its a pretty simple, yet extremely effective workflow, and it saves you a lot of context window usage from your main agent:

1. Define your task in detail (set standards, behavior patterns) and specifically request that your main agents uses their #runSubagent tool. 
2. Main agent delegates the task to the required subagent instances
3. The subagent instances do the context-intensive work and return a concise report to the calling agent
4. The calling agent only integrates the report and saves context

  
Pretty simple, yet so effective. Its still in early stages with limited capabilities, but just for these 3 tasks i describe above its super efficient. Kinda like what [APM](https://github.com/sdi2200262/agentic-project-management) does with Ad-Hoc Agents, without using separate Agent instances.


## Top comments (by score)

### 1. (7) u/Infinite-Ad-8456

It'd be better and insanely useful if I can do executions in parallel instead of IT being plain sequential. That way I can designate async tasks and wrap up work more efficiently...

link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nytbf5x/

### 2. (7) u/Cobuter_Man

  there are background agents for that, except for that case you would need to have an orchestration pipeline and work trees etc.  Other platforms have similar workflows but at the end of the day you never get far because unsupervised agents are not as good as it sounds atm.

  link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nytnlla/

### 3. (6) u/MhaWTHoR

thats exactly how I use it.

The subagents with no request drop also an awesome thing.

link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nyvnbhy/

### 4. (4) u/humantriangle

I also use sub agents for tool management, using custom sub agents. Meaning I can have more tools overall, but not litter my main agent with tools only used for, say, research.

link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nyxtn6y/

### 5. (3) u/iloveapi

can you share your agent instruction? thanks

link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nyybouo/

### 6. (3) u/Cobuter_Man

  not 100% sure, but i think it is part of the same request turn so no.

If you export a chat as a JSON transcript you will see that #runSubagent is only registered as a tool within a turn, so i think it counts as a 0x multiplier

  link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nyvqean/

### 7. (3) u/humantriangle

  No, they don’t

  link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nyxtg1o/

### 8. (2) u/Otherwise-Way1316

Does each subagent consume its own premium request?

link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nyvoay7/

### 9. (2) u/MoxoPixel

I have no idea how to use this. Can I just write "use subagents to research codebase before applying code from user prompt" in AGENTS.md or something?

link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nz21zrd/

### 10. (2) u/Cobuter_Man

  I dont have a particular instruction file as I use subagents for ad-hoc tasks. The general workflow is almost identical to what i describe in the post, and my prompt is mostly as simple as my description in the post. However, i use either Sonnet 4.5 or Opus 4.5 that have great agentic capabilities so perhaps in less capable models you would have to be a bit more precise

  link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nyygfko/

### 11. (1) u/digitarald

Team member here, thanks for the great write up . Great content that we should bring into the docs.

We are working on parallel subagents this iteration, which should unblock a bunch of interesting use cases. Upcoming is also default-enabling use of custom agents with subagents, and that subagents can be initialized with a specific model.

Any other feedback for agent primitives like custom agents, subagents and skills?

link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nz2s7l6/

### 12. (1) u/codehz

  I think it will no longer "free" if it support parallel... (This will obviously accelerate token consumption significantly..)

  link: https://www.reddit.com/r/GithubCopilot/comments/1q90cq5/how_to_effectively_use_subagents_in_copilot/nz3f7pz/
