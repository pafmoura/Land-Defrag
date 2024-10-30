import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SimulatorsetupComponent } from './simulatorsetup.component';

describe('SimulatorsetupComponent', () => {
  let component: SimulatorsetupComponent;
  let fixture: ComponentFixture<SimulatorsetupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimulatorsetupComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SimulatorsetupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
