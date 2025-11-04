const { cloneArray, subtract, sum } = require('./test_function.js');

test('testing the sum function', () => {
  expect(sum(2, 3)).toBe(5)
})

test('testing the subcract function', () => {
    expect(subtract(5, 2)).toBe(3)
})

test('testing the cloning function', () => {
    expect(cloneArray([1,2])).toEqual([1,2])
})

