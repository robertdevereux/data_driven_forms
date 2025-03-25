<h2>Public services</h2>

Public services is a broad term. For the most part (leaving aside eg provision of advice), they enable
- citizens and organisations 
- to secure their entitlements (a grant, a benefit, an authorisation)
- or to settle their liabilities (a tax, a parking fine)

Entitlements and liabilities usually 
- require information from the citizen / organisation
- a decision on entitlement / liability (and the amount)
- a fulfilment of the entitlement (a payment out, a new passport)
- a settling of a liability (a payment in, a child maintenance payment to a parent)

We will use the term "regime" to mean a self contained service

In some cases, a service might consist of a set of similar/related regimes
- for example, Customs Authorisations might be considered to be a single service
- comprising one regime for each individual authorisation
- with some sharing of data, and some conditionality (this auth only if that auth)

<h2>Regime data</h2>

All of the regimes we have seen rely on gathering data from the citizen / company. That data can be more of less extensive.  

We want to be able to re-use questions between regimes. So we will use
- a QUESTION object 
- to hold relevant details for each question (the text, a hint, the question_type etc)

Some of the questions asked in one regime are also asked in other regimes. Such questions
- either logically result in the same answer, across all regimes (eg DoB): so they can be driven by the same question in QUESTION
- or may result in different answers (eg the mode of transport for an export authorisation may differ between differnt auths): which will require different questions in QUESTION

The number of questions in each regime varies considerably, from a few to hundreds. For ease of use, we will use
- a SECTION object to record groups of related questions, typically <15 per section so that they fit in the typical GDS confirmation screen
- a SCHEDULE object to record groups of related sections, typically <8 for ease of navigation

An individual regime will then be defined by
- EITHER one <i>section</i> of <i>questions<\i> 
- OR one set of <i>sections</i> 
- OR a set of <i>schedules</i>, each containing a set of questions (as many schedules as needed)
All of which can be captured in the QUESTION, SECTION and SCHEDULE objects


<h2>Access controls</h2>

Many regimes operate only for individual citizens, acting without intermediaries.

But we need also to cater for
- different employees within an organisation acting for the organisation
- for individual third parties (eg a solicitor, an accountant) acting for an individual or an organisation
- for different employees of a third party (an accountancy firm) acting on behalf of an individual or organisation 

In many cases, each of the individuals above might be given access to all the customer data within a regime.

But we need to allow for more restrictive permissions: 
- where an individual allows the intermediary to see only some of their regime data
- where a company allows some of it employees to see only some of the company regime data
- where company allows an intermediary to see only some of its regime data
- where an intermediary company in turn wants to allow some of its employees to see only some of the data the intermediary can see.

This level of complexity would rapidly become unmanageable if operated at the level of each question: potentially hundreds of permissions to be set.

So we will instead build on the structure above, and define
- a PERMISSION object
- recording which individuals can see which sections

To cater for employees within organisations, we need
- to record one name within an organisation
- who has the right to create permissions within that organisation
- who has the right to create permissions within an intermediary
- and who can determine whether the permissions they grant can be used to create further permissions (eg to cascade down a hierarchy)

That way, 
- Ms X in CompanyA would provide permissions to Mr A, Mrs B, and Ms C inside CompanyA, and allowing Ms C only to delegate her permissions
- Ms C could the delegate permissions to Mr D and Ms E, with no delegation rights
- Mr X could also provide permission to Ms F at KPMG in respect of Corporation Tax with delegation rights
- Mr F could provide permission to his colleagues Ms G and Mr H within KPMG.

With individual permissions set in this way, a user would see only the regimes, schedules, and sections to which they have access<br>

<h2>The high level process</h2>

On a successful login, the user name is used to create a list of regime this user can see, presented as options to choose<br>

On choosing a regime, the user name and chosen regime is used to create a list of regime schedules this user can see, presented as options to choose<br>

On choosing a schedule, the user name and chosen schedule is used to create a list of sections which the user can see, presented as options to choose.

On choosing a section, the app finds the relevant routing, and begins to run through the questions/routing.
