/**
 * Farm selector component for switching between different farms
 */
import './FarmSelector.css'

const FarmSelector = ({ farms, selectedFarm, onSelectFarm }) => {
    return (
        <div className='farm-selector'>
            <div className='farm-tabs'>
                {farms.map((farm) => (
                    <button
                        key={farm.id}
                        className={`farm-tab ${selectedFarm === farm.id ? 'active' : ''}`}
                        onClick={() => onSelectFarm(farm.id)}
                    >
                        <span className='farm-name'>{farm.name}</span>
                        <span className='farm-location'>{farm.location}</span>
                    </button>
                ))}
            </div>
        </div>
    )
}

export default FarmSelector
