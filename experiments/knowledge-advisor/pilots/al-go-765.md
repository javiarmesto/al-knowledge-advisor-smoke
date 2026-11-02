# Test are always run with codeunit Test Runner - Isol. Codeunit

Source: https://github.com/microsoft/AL-Go/issues/765
Scope: public issue title and body as retrieved on 2026-11-02; discussion withheld for comparison.

When the tests are run in the pipelines all tests are kicked of with the codeunit "Test Runner - Isol. Codeunit".
Only if you want to test the API's you must use "Test Runner - Isol. Disabled".
So it would be very helpfull that you can define in the pipeline or something else which test are runing with the isolation codeunit and some tests with the isolation disabled.
Otherwise you cannot test your API's because you must commit a value into the database when you do a GET request.

Moslty you run first all the test with the isolation codeunit and after those are finished you have to run the tests with isolation disabled.
