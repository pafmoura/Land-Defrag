import { TestBed } from '@angular/core/testing';

import { GeoJsonUtilsService } from './geo-json-utils.service';

describe('GeoJsonUtilsService', () => {
  let service: GeoJsonUtilsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GeoJsonUtilsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
