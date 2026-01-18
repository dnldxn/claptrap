# The Ralph-Wiggum Loop

- subreddit: r/ClaudeCode
- author: u/TrebleRebel8788
- score: 45
- num_comments: 61
- url: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/
- permalink: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/

## Post body

So I’m pretty sure those who know, know. If you don’t, cause I just found this working on advanced subagents, and it tied into what I was working on. 

Basic concept, agent w/ sub-agents + a python function forcing the agent to repeat the same prompt over and over autonomously improving a feature. You can set max loops, & customize however you want.

I’m building 4 now, and have used 2. It works, almost too well for my 2 agents. Does anyone else know about this yet and if so, what do you use it for, any hurdles or bugs in it, failures, etc? We say game changers a lot…this is possibly one of my favorites.


## Top comments (by score)

### 1. (35) u/zbignew

  I had a bug that was only coming up in CI and I didn’t know why I couldn’t replicate it locally.

Claude was lost too and fiddling with random isht and often stopping, as I would normally want it to, checking in with me before pushing. And then it takes a couple minutes to see the failing tests, and Claude is a little slow noticing the CI is complete. 

So I did 

```
/ralph-wiggum:start figure out why ci step 4 is failing even though it works when i do make update locally
```

And walked away and read books to my 6yo for 90 minutes.

Claude had fixed the problem like 10 minutes prior and it went nuts after being pestered for those additional 10 minutes and it was paused, requesting permission to delete the Ralph Wiggum plugin from `~/.claude/`

  link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxv98d/

### 2. (23) u/s0m3d00dy0

Do you guys not have usage limits?

link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxnf8a/

### 3. (19) u/notDonaldGlover2

I need someone to dumb down an example for me.

link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxn7c7/

### 4. (13) u/Ok_Presentation_5489

  That's what I was thinking, doesn't this burn tokens like crazy?

  link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxqqz0/

### 5. (13) u/s0m3d00dy0

    I need someone to dumb down an example for me.

    link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxsa50/

### 6. (12) u/sgt_brutal

Basically, all I do is chain while loops with a scoring/evaluation function that analyzes the agent's progress against a set of weighted parameters. 


This pattern is so versatile that it makes up over 90% of my agent designs. That is, I explicitly start from this Ralph/WPQ chain, and most of the time I end up simplifying the construct to a single alternation of these two fundamental blocks. 


Simple workflows don't require deploying a codified WPQ, as the context is relatively short for the agent to stay sane and the criteria for phase-transition are few - a single-context agent can handle its function.

link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxf32v/

### 7. (12) u/Trotskyist

  The most basic version is essentially: 

1) Define success criteria for [thing]
2) Attempt to do [thing]
3) Check if success criteria from step 1 is met, if so, stop. Otherwise,
4) Pick up the codebase where step 2 left off, and try to do [thing] again

Repeat steps 2-4 until done.

  link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxy6jj/

### 8. (8) u/PerformanceSevere672

  it actually doesn't get dumber than ralph wiggum, that's the point

  link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxs6kf/

### 9. (8) u/eduo

    The end of this comment sent me 😂

    link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyytrk9/

### 10. (6) u/Fenzik

Anthropic’s default plugin marketplace has a plugin for this: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum

But I’m not gonna lie I don’t really _get_  it

link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyxwe57/

### 11. (5) u/positivitittie

I’m trying it for the first time tonight. Had Claude make a custom version (Milhouse) and I make it consult other LLMs during its loop after previous loop findings, to come to consensus on the plan for the upcoming code.

Seems like it has it’ll be useful for certain tasks anyway.

With some improvement it I feel like it could be made pretty good. Definitely gonna keep it in my toolbox.

link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyx7qq4/

### 12. (5) u/BootyMcStuffins

  No, my company pays for it. I actually get put on a leaderboard for using more tokens. It’s ridiculous

  link: https://www.reddit.com/r/ClaudeCode/comments/1q9qjk4/the_ralphwiggum_loop/nyyxzzq/
