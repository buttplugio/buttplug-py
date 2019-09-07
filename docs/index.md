## Introduction

buttplug-py is a Python 3 implementation of the client portion of the
Buttplug Intimate Hardware Protocol. For more information on the
protocol, see the project website at

https://buttplug.io

You may also be interested in the Buttplug Spec at

https://buttplug-spec.docs.buttplug.io

and the Buttplug Developer Guide, at 

https://buttplug-developer-guide.docs.buttplug.io

## What Client Only Means

buttplug-py is only an implementation of the client side of the
Buttplug Protocol. Programs written with this client cannot directly
access hardware, and will be required to connect to a Buttplug Server,
such as Intiface Desktop in order to access hardware. You can find
more information on Intiface Desktop at

https://intiface.com/desktop

## Python Notes

Before discussing the basics of using buttplug-py, we'll cover a few
things to consider when implementing applications with it.

- buttplug-py is HEAVILY Python 3.7. asyncio, dataclasses, typings,
  all that fun stuff. I (qDot, the author) have no plans on
  backporting, because I love these features and just plain don't
  wanna.
- If someone else wants to backport for < 3.7 (but still >= 3 because
  come on 2.7 EOLs in like 3 months), please feel free to get in
  touch. I'm just not gonna do it myself.
- At the moment, only the Client and ClientDevice classes are
  documented and meant to be used. Most of the protocol messages are
  available in code, but if you go that direction, you're on your own.
- In order to make it look similar to the other implementations of the
  Buttplug protocol (such as
  [C#](https://github.com/buttplugio/buttplug-cshar) and
  [Typescript/Javascript](https://github.com/buttplugio/buttplug-js)),
  there is a faux-event system in buttplug-py. It's basically a way to
  attach callbacks to a list to be called at a certain time. Examples
  of this will be shown in the Usage section below.

Event Handling looks similar to C#, with the ability to use the +=/-=
operators on EventHandler types to add/remove handlers. See the
example code below for demonstration of how event hookup works.
