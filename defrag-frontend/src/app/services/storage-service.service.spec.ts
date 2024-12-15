import { TestBed } from '@angular/core/testing';

import { StorageService } from './storage-service.service';

describe('StorageServiceService', () => {
  let service: StorageService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StorageService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('should add and retrive a test value', () => {
    service.setItem("unit_test", true)
    expect(service.getItem("unit_test")).toBeTrue();
  });
});
