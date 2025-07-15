'use client';

import { useRouter } from 'next/navigation';
import { useWorkflow, WorkflowStep, stepMetadata } from '@/contexts/WorkflowContext';

interface WorkflowStepperProps {
  className?: string;
  showLabels?: boolean;
}

export function WorkflowStepper({ className = '', showLabels = true }: WorkflowStepperProps) {
  const { state, actions } = useWorkflow();
  const router = useRouter();

  const steps: WorkflowStep[] = ['keyword', 'title', 'content', 'publish'];

  const handleStepClick = (step: WorkflowStep) => {
    if (actions.canGoToStep(step)) {
      actions.setStep(step);
      router.push(stepMetadata[step].path);
    }
  };

  const getStepStatus = (step: WorkflowStep) => {
    const stepIndex = steps.indexOf(step);
    const currentStepIndex = steps.indexOf(state.currentStep);

    if (stepIndex < currentStepIndex) {
      return 'completed';
    } else if (stepIndex === currentStepIndex) {
      return 'current';
    } else {
      return actions.canGoToStep(step) ? 'available' : 'disabled';
    }
  };

  const getStepClasses = (step: WorkflowStep) => {
    const status = getStepStatus(step);
    const baseClasses = 'flex items-center justify-center w-10 h-10 rounded-full font-medium text-sm transition-all duration-200 cursor-pointer';

    switch (status) {
      case 'completed':
        return `${baseClasses} bg-green-600 text-white hover:bg-green-700`;
      case 'current':
        return `${baseClasses} bg-blue-600 text-white ring-4 ring-blue-200`;
      case 'available':
        return `${baseClasses} bg-gray-200 text-gray-700 hover:bg-gray-300`;
      case 'disabled':
        return `${baseClasses} bg-gray-100 text-gray-400 cursor-not-allowed`;
      default:
        return baseClasses;
    }
  };

  const getConnectorClasses = (stepIndex: number) => {
    const currentStepIndex = steps.indexOf(state.currentStep);
    const isCompleted = stepIndex < currentStepIndex;
    
    return `flex-1 h-1 mx-2 rounded-full transition-all duration-300 ${
      isCompleted ? 'bg-green-600' : 'bg-gray-200'
    }`;
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">콘텐츠 생성 워크플로우</h2>
        <div className="text-sm text-gray-600">
          진행률: {actions.getStepProgress()}%
        </div>
      </div>

      {/* 진행률 바 */}
      <div className="mb-6">
        <div className="bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${actions.getStepProgress()}%` }}
          />
        </div>
      </div>

      {/* 스테퍼 */}
      <div className="flex items-center">
        {steps.map((step, index) => (
          <div key={step} className="flex items-center flex-1">
            {/* 스텝 원 */}
            <div 
              className={getStepClasses(step)}
              onClick={() => handleStepClick(step)}
              role="button"
              tabIndex={actions.canGoToStep(step) ? 0 : -1}
              aria-label={`${stepMetadata[step].title} 단계`}
              onKeyDown={(e) => {
                if ((e.key === 'Enter' || e.key === ' ') && actions.canGoToStep(step)) {
                  e.preventDefault();
                  handleStepClick(step);
                }
              }}
            >
              {getStepStatus(step) === 'completed' ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                <span>{stepMetadata[step].icon}</span>
              )}
            </div>

            {/* 연결선 */}
            {index < steps.length - 1 && (
              <div className={getConnectorClasses(index)} />
            )}
          </div>
        ))}
      </div>

      {/* 스텝 라벨 */}
      {showLabels && (
        <div className="flex items-start mt-4">
          {steps.map((step, index) => (
            <div key={step} className="flex-1 text-center">
              <div className="text-sm font-medium text-gray-900">
                {stepMetadata[step].title}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stepMetadata[step].description}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 현재 단계 정보 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{stepMetadata[state.currentStep].icon}</span>
          <div>
            <h3 className="font-medium text-blue-900">
              현재 단계: {stepMetadata[state.currentStep].title}
            </h3>
            <p className="text-sm text-blue-700">
              {stepMetadata[state.currentStep].description}
            </p>
          </div>
        </div>

        {/* 네비게이션 버튼 */}
        <div className="flex justify-between mt-4">
          <button
            onClick={actions.goToPreviousStep}
            disabled={state.currentStep === 'keyword'}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← 이전 단계
          </button>

          <div className="flex gap-2">
            <button
              onClick={actions.resetWorkflow}
              className="px-4 py-2 text-sm font-medium text-red-700 bg-white border border-red-300 rounded-md hover:bg-red-50"
            >
              처음부터
            </button>
            
            <button
              onClick={actions.goToNextStep}
              disabled={!actions.canGoToStep(steps[steps.indexOf(state.currentStep) + 1])}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              다음 단계 →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WorkflowStepper;