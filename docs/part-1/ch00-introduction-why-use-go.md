## Chapter 0: Introduction & Why Use Go

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-00-intro-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-00-intro-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="iDQAZEJK8lI" chapter="00" />

Before I get into Go, I'd like to answer the question: why use Go?

There are really a couple of reasons to pick Go. One is that it's a simple and readable language that makes software engineering easier. The other is that it makes software perform better in the cloud.

### Software Engineering

Let me talk about the software engineering part first. What is software engineering? Well, it's really about programming in the large — programming with lots of time and lots of people. We need programs that are reliable and maintainable. We need to be able to change them over the years. We need to go back and read what we wrote in the past. We need to be able to hire new people and have them come on and understand our programs quickly. We don't want to be clever.

There's a phrase, "to out-clever yourself," and it really reminds me of the Roadrunner cartoon. Wile E. Coyote, Super Genius — he's constantly building traps to try to catch the Road Runner, usually with dynamite, and constantly blowing himself up. We don't want to go down that road. That's why we want to do things that are simple. Simplicity is the key to building good software.

To do that, it's not enough to write a simple program — we need to use a language that's simple and readable, because we spend a lot of time reading programs. A lot of languages like C++ just keep growing. Every few years a whole bunch more features get dumped in, and over time it just becomes harder and harder to understand, or you get different versions of code written in different versions of the language.

Go was designed from the get-go to be easy to use. It was designed, as this quote says from the original Go FAQ, to be as easy to use as some dynamically typed interpreted languages but to have the safety and speed of a compiled language.

Simplicity has been one of the key design criteria from the beginning, and the focus of the last ten or eleven years has been on keeping it simple and improving the runtime and the tools — making garbage collection better, not dumping new features into the language.

I really want to call out this quote by Erik that Go is a language that fits in your head. The benefit of that is instead of using a language subset or constantly turning to experts, Go is a language that's open to new people coming into the field. It's a language that's easy to learn and easy to use, and actually perfectly suitable as an introductory programming language for learning to code.

John Bodner wrote this blog post, "Go is Boring," and it turned into a GopherCon 2020 presentation. The key point is that simplicity is a key language feature all by itself. We talk about does the language have this or that or the other, but it's really about what the language *doesn't* have that helps make it so powerful.

### Performance in the Cloud

Now I want to flip to the other side and talk about the changes that have happened over the last fifteen years. If I draw a line on this chart about 2005, we see that cores don't get faster — instead we get more cores per CPU.

Unfortunately, a lot of the languages and techniques for building software that we have come from the other side of this line. The popular languages today — and it doesn't matter the order, it depends on what survey you look at — they're all about twenty years old or more. We can actually even say they're from the last century. They date from a time when machines had one CPU with one core, they were getting faster every year, and concurrency and distributed programming were research topics, not practical necessities.

Going forward, there's really only a couple of ways to make software faster. We can either make it concurrent to take advantage of those cores, or we can make it suck less — and by that I really mean we can waste less.

There's a saying that "the cloud doesn't exist — it's just somebody else's computer." Well, yes, and my point would be you rent it by the hour, by the second, whatever. So if Go can run significantly faster — and against some languages we're talking an order of magnitude faster — you're going to save an enormous amount of rent.

I don't want to point the finger at any particular language (in this case it's Ruby), but if you look at some of the interpreted languages — when I was younger, back in the '80s, nobody would have built production software in an interpreted language. Then over time we ended up with CPU cycles we thought we could waste. The reality is we can't waste them anymore, and so it's probably time to go back and think about: yes, we do want software that's simple, but we also want software that doesn't waste.

### Go in the Cloud

Go is becoming the go-to language for cloud development, particularly infrastructure but also apps. Performance is one aspect. There's another one, and that is that Go is simple to deploy. You can put a Go program by itself in a container. You don't need a JVM or an interpreter. You don't need libc or the rest of what typically shows up in an operating system. What that means is the container is very small, and it's also going to be more secure because you've just left out an enormous source of vulnerabilities.

I think this quote from the Bitly engineering blog really helps drive some of the key points here: it's a language that's easy to use, it's fast, it's safe, and it comes with tools that make software engineering easier. Now, I can't promise that Bitly is still doing Go or is still excited — time moves on — but I think it was a really good blog article when it was written, because it captures the things that are still true today, that these things are still valuable when you contrast Go against some of the other popular languages for cloud development.

I want to offer you this quote from the late Dennis Ritchie, inventor of the C language:

> *"A programming language that doesn't have everything can be easier to use than one that does."*

I think that's again a pretty valuable reason to pick Go.

---
