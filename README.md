<h1>Data structure and access controls</h1>

<h2>Data</h2>

At the top level are <b>regimes</b>, which might be a single tax or a welfare benefit or a driving licence<br>

Each regime is comprised of <b>schedules</b>, say the bank account schedule of IHT, or medical conditions on a PIP claim<br>

Each schedule is comprised of <b>sections</b>, which represent groups of related questions/data within a schedule<br>

<h2>Access controls</h2>

A permissions object records which users can see which regimes, schedules and sections.

Using these permissions, a user sees only the regimes, schedules, and sections to which they have access<br>

<h2>The high level process</h2>

On a successful login, the user name is used to create a list of regime this user can see, presented as options to choose<br>

On choosing a regime, the user name and chosen regime is used to create a list of regime schedules this user can see, presented as options to choose<br>

On choosing a schedule, the user name and chosen schedule is used to create a list of sections which the user can see, presented as options to choose.

On choosing a section, the app finds the relevant routing, and begins to run through the questions/routing.
