import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcessqueueComponent } from './processqueue.component';

describe('ProcessqueueComponent', () => {
  let component: ProcessqueueComponent;
  let fixture: ComponentFixture<ProcessqueueComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcessqueueComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProcessqueueComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
