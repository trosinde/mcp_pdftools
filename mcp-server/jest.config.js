export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1',
  },
  transform: {
    '^.+\\.ts$': [
      'ts-jest',
      {
        useESM: true,
      },
    ],
  },
  testMatch: [
    '**/tests/**/*.test.ts',
  ],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    // v1.0: Critical security paths only (validator, security modules)
    // v1.1: Will add tool handlers, executor, config tests
    './src/utils/validator.ts': {
      branches: 70,
      functions: 50,
      lines: 50,
      statements: 50,
    },
    './src/utils/security.ts': {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
