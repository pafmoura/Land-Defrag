import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatisticsModalComponent } from './statistics-modal.component';

describe('StatisticsModalComponent', () => {
  let component: StatisticsModalComponent;
  let fixture: ComponentFixture<StatisticsModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StatisticsModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StatisticsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('check if initial simulation exists', () => {
    expect(component.initialSimulation).toBeTruthy();
  });

  //describe('should calculate owner areas', () => {
  //  expect(component.calculateOwnerAreas(component.initialSimulation)).toBeTruthy();
  //});
});
