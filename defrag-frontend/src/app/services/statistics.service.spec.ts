import { TestBed } from '@angular/core/testing';

import { StatisticsService } from './statistics.service';

describe('StatisticsService', () => {
  let service: StatisticsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StatisticsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('get results data', () => {
    expect(service.getResultsData()).toBeTruthy();
  });

  describe('get initial simulation', () => {
    expect(service.getInitialSimulation()).toBeTruthy();
  });

  describe('get basic statistics', () => {
    expect(service.generateBasicStatistics(service.getResultsData(), service.getInitialSimulation())).toBeTruthy();
  });
});
